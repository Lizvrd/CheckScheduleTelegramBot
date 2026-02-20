from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import F
from configBot import bot
import keyboards
from dotenv import load_dotenv
import os
from tables.check_exist_groups import check_exist_groups
from tables.schedule_manager import get_today_schedule, get_tomorrow_schedule, get_week_schedule

load_dotenv()

privateChatRouter = Router()

@privateChatRouter.message(CommandStart())
async def startChat(message: Message) -> None:
    await bot.send_photo(message.from_user.id, photo=os.getenv("SAY_HELLO_PHOTO_LINK"), caption=f"Привет, студент!\n\nЧтобы начать работу с ботом, напиши свою группу.\nПримеры: Б12-345-6\nб12-345-6")

@privateChatRouter.message(F.text)
async def start(message: Message) -> None:    
    user_text = message.text
    
    if await check_exist_groups(user_text=user_text) == False:
        await bot.send_photo(message.from_user.id, photo=os.getenv("NOT_FOUND_GROUP_LINK"), caption=f"Группа <i>{user_text}</i> не найдена. Возможно, что вы ввели неправильное название группы.\nПроверьте правильность ввода.\nПримеры: Б12-345-6\nб12-345-6")
        return

    await bot.send_photo(message.from_user.id, photo=os.getenv("GROUP_IS_FOUND_LINK"), caption=f"Привет, студент! 🎓\nЯ тут, чтобы ты никогда не опоздал на пару (ну, почти никогда).\nЧто могу:\n✓ Показать расписание твоей группы на любой день.\n✓ Найти, где и когда ведёт занятия нужный препод.\n✓ Напомнить о парах (включи уведомления!).\n✓ Данные расписания обновлются автоматически при изменении анализе даты на сайте.\n\nЯ открытый проект — мой код на GitHub: <a href='https://github.com/Lizvrd/CheckScheduleTelegramBot'>GitHub</a>!  \nА теперь давай найдём твои занятия! Жми «Расписание» 👇",reply_markup=keyboards.start_keyboard())    

@privateChatRouter.callback_query(lambda call: call.data == "get_schedule")
async def get_schedule(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption="Для получения расписания нужно выбрать режим работы. Выбери режим вывода:", reply_markup=keyboards.choice_mode_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "today")
async def send_today_schedule(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption=f"Расписание на сегодня: ", reply_markup=keyboards.today_schedule_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "tomorrow")
async def send_tomorrow_schedule(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption="Расписание на завтра:", reply_markup=keyboards.tomorrow_schedule_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "week")
async def send_week_schedule(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption="Расписание на неделю:", reply_markup=keyboards.week_schedule_keyboard())