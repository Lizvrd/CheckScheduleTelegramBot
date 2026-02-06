from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from configBot import bot
import keyboards
from dotenv import load_dotenv
import os
load_dotenv()

privateChatRouter = Router()

@privateChatRouter.message(CommandStart())
async def start(message: Message) -> None:
    if message.from_user.username != "skndcfck":
        return
    else:
        await bot.send_photo(message.from_user.id, photo=os.getenv("SAY_HELLO_PHOTO_LINK"), caption=f"Привет, студент! 🎓\nЯ тут, чтобы ты никогда не опоздал на пару (ну, почти никогда).\nЧто могу:\n✓ Показать расписание твоей группы на любой день.\n✓ Найти, где и когда ведёт занятия нужный препод.\n✓ Напомнить о парах (включи уведомления!).\n✓ Данные расписания обновлются автоматически при изменении анализе даты на сайте.\n\nЯ открытый проект — мой код на GitHub: [ссылка].  \nА теперь давай найдём твои занятия! Жми «Расписание» 👇",reply_markup=keyboards.start_keyboard())
        
        # await message.answer(f"Привет, студент! 🎓\nЯ тут, чтобы ты никогда не опоздал на пару (ну, почти никогда).\nЧто могу:\n✓ Показать расписание твоей группы на любой день.\n✓ Найти, где и когда ведёт занятия нужный препод.\n✓ Напомнить о парах (включи уведомления!).\n✓ Данные расписания обновлются автоматически при изменении анализе даты на сайте.\n\nЯ открытый проект — мой код на GitHub: [ссылка].  \nА теперь давай найдём твои занятия! Жми «Расписание» 👇", reply_markup=keyboards.start_keyboard())
        
@privateChatRouter.callback_query(lambda call: call.data == "get_schedule")
async def get_schedule(callback: CallbackQuery) -> None:
    await callback.message.edit_caption("Для получения расписания нужно выбрать режим работы. Выбери режим вывода:", reply_markup=keyboards.choice_mode_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "today")
async def today(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(text="Расписание на сегодня:", reply_markup=keyboards.today_schedule_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "current_day")
async def current_day(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(text="Для отображения расписания на определенный день выбери день(автоматически будет определено какая неделя: над чертой или под чертой):", reply_markup=keyboards.current_day_schedule_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "week")
async def week(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(text="Расписание на неделю:", reply_markup=keyboards.week_schedule_keyboard())