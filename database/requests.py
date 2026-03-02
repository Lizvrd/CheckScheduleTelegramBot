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
      
async def get_all_unique_groups_users():
    async with async_session() as session:
        query = select(User.group).where(User.group != None).distinct()
        result = await session.execute(query)
        return result.scalars().all()
    
async def add_lesson_to_db(group_name, day_name, start_time, subject, audience, week_type, teacher):
    async with async_session() as session:
        lesson = Lesson(
            group_name = group_name,
            day_name = day_name,
            start_time = start_time,
            subject = subject,
            teacher = teacher,
            audience = audience,
            week_type = week_type
        )
        session.add(lesson)
        await session.commit()

# Where is teacher
async def find_teacher(teacher_name: str, day: str, week_type: int):
    async with async_session() as session:
        query = select(Lesson).where(Lesson.teacher.ilike(f"%{teacher_name}%"),Lesson.day_name == day, Lesson.week_type == week_type).order_by(Lesson.start_time)
        
        result = await session.execute(query)
        return result.scalars().all()
        

# Очищаем все данные из таблиц с сохраненными расписаниями и парами
async def clean_all_schedules():
    async with async_session() as session:
        await session.execute(delete(CacheSchedule))
        await session.execute(delete(Lesson))
        await session.commit()

async def get_lessons_for_group_day(group: str, day: str, week_type: int):
    """Получает все пары группы на конкретный день для поиска первой пары"""
    async with async_session() as session:
        query = select(Lesson).where(
            Lesson.group_name == group,
            Lesson.day_name == day,
            Lesson.week_type == week_type
        )
        result = await session.execute(query)
        return result.scalars().all()
        
async def get_lesson_for_notification(group: str, day: str, week_type: int, time_str: str):
    """Поиск конкретного урока для уведомления"""
    async with async_session() as session:
        query = select(Lesson).where(
            Lesson.group_name == group,
            Lesson.day_name == day,
            Lesson.week_type == week_type,
            Lesson.start_time == time_str
        )
        result = await session.execute(query)
        return result.scalar()