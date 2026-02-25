from .models import User, async_session
from sqlalchemy import select, update

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
    