import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from private_chat import privateChatRouter
from configBot import bot
import logging, sys

dp = Dispatcher(storage=MemoryStorage())

async def main() -> None:
    dp.include_router(privateChatRouter)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())