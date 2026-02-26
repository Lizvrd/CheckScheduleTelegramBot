import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging, sys
from configBot import bot
from private_chat import privateChatRouter
from tables.schedule_manager import migrate_data_to_db
from database.models import async_main

dp = Dispatcher(storage=MemoryStorage())

async def main() -> None:
    await async_main()
    await migrate_data_to_db()
    dp.include_router(privateChatRouter)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())