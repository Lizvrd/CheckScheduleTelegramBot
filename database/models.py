import asyncio
from sqlalchemy import String, BigInteger, Integer, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite:///quant_database.db', echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs,DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    group: Mapped[str] = mapped_column(String, nullable=True)

class CacheSchedule(Base):
    __tablename__ = 'cached_schedules'

    group_name: Mapped[str] = mapped_column(String, primary_key=True)
    schedule_data: Mapped[str] = mapped_column(String)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    print("🦊База кванта успешно инициализирована")
    asyncio.run(async_main())