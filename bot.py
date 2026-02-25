import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from private_chat import privateChatRouter
from tables.schedule_manager import update_groups_cache
from configBot import bot
import logging, sys
from database.models import async_main

dp = Dispatcher(storage=MemoryStorage())

async def main() -> None:
    await async_main()
    await update_groups_cache()
    dp.include_router(privateChatRouter)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())