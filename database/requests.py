from .models import User, async_session, CacheSchedule, UserSettings, Lesson
from sqlalchemy import select, update, delete

#User
async def set_user(tg_id: int, username: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        if not user:
            session.add(User(telegram_id=tg_id, username=username))
            await session.commit()
            
async def update_user_group(tg_id: int, group: str):
    async with async_session() as session:
        await session.execute(update(User).where(User.telegram_id == tg_id).values(group=group.upper()))
        await session.commit()

async def get_user_group(tg_id: int) -> str | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        return user.group if user else None

#CacheSchedule
async def save_cached_schedule(group: str, text: str):
    async with async_session() as session:
        new_cache = CacheSchedule(group_name=group.upper(), schedule_data=text)
        await session.merge(new_cache)
        await session.commit()
        
async def get_cached_schedule(group: str):
    async with async_session() as session:
        result = await session.execute(select(CacheSchedule.schedule_data).where(CacheSchedule.group_name == group.upper()).limit(1))
        return result.scalar()
    
async def is_cache_empty():
    async with async_session() as session:
        result = await session.execute(select(CacheSchedule).limit(1))
        return result.scalar() is None
    
#Settings
async def get_user_settings(tg_id: int):
    async with async_session() as session:
        settings = await session.scalar(select(UserSettings).where(UserSettings.telegram_id == tg_id))
        if not settings:
            new_settings = UserSettings(telegram_id=tg_id)
            session.add(new_settings)
            await session.commit()
            return new_settings
        return settings
    
async def edit_settings(tg_id: int, key: str, value):
    async with async_session() as session:
        settings = await session.scalar(select(UserSettings).where(UserSettings.telegram_id == tg_id))
        if settings:
            setattr(settings,key,value)
            await session.commit()
            
async def cycle_edit_time(tg_id: int):
    async with async_session() as session:
        settings = await session.scalar(select(UserSettings).where(UserSettings.telegram_id == tg_id))
        if settings:
            times = [30,60,90,120]
            current_index = times.index(settings.time_offset)
            new_time = times[(current_index+1) % len(times)]
            settings.time_offset = new_time
            await session.commit()
            return new_time

#Notifications        
async def get_users_for_notifications():
    async with async_session() as session:
        query = select(UserSettings, User.group).join(User, User.telegram_id == UserSettings.telegram_id).where(UserSettings.is_active == True)
        result = await session.execute(query)
        return result.all()
      
async def get_all_unique_groups_users(telegram_id: int):
    async with async_session() as session:
        query = select(User).where(User.group != None).distinct()
        result = await session.execute(query)
        return [row[0] for row in result.all()]
    
async def clear_lessons():
    async with async_session() as session:
        await session.execute(delete(Lesson))
        await session.commit()
        
async def add_lesson_to_db(group_name, day_name, start_time, subject, audience, week_type):
    async with async_session() as session:
        lesson = Lesson(
            group_name = group_name,
            day_name = day_name,
            start_time = start_time,
            subject = subject,
            audience = audience,
            week_type = week_type
        )
        session.add(lesson)
        await session.commit()