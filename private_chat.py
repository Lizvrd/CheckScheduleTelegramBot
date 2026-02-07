from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import F
from configBot import bot
import keyboards
from dotenv import load_dotenv
import os
from check_validate import validate_group_format

load_dotenv()

privateChatRouter = Router()

@privateChatRouter.message(CommandStart())
async def startChat(message: Message) -> None:
    if message.from_user.username != "skndcfck":
        return
    else:
        await bot.send_photo(message.from_user.id, photo=os.getenv("SAY_HELLO_PHOTO_LINK"), caption=f"Привет, студент!\n\nЧтобы начать работу с ботом, напиши свою группу.\nПримеры: Б12-345-6\nб12-345-6")

@privateChatRouter.message(F.text)
async def start(message: Message) -> None:
    if (validate_group_format(text=message.text) == False) and (len(message.text) == 9):
        await message.answer("Неверный формат группы. Попробуй еще раз.\nПримеры: Б12-345-6\nб12-345-6")
    elif len(message.text) != 9:
        return
    elif (validate_group_format(text=message.text) == True):
        await bot.send_photo(message.from_user.id, photo=os.getenv("SAY_HELLO_PHOTO_LINK"), caption=f"Привет, студент! 🎓\nЯ тут, чтобы ты никогда не опоздал на пару (ну, почти никогда).\nЧто могу:\n✓ Показать расписание твоей группы на любой день.\n✓ Найти, где и когда ведёт занятия нужный препод.\n✓ Напомнить о парах (включи уведомления!).\n✓ Данные расписания обновлются автоматически при изменении анализе даты на сайте.\n\nЯ открытый проект — мой код на GitHub: [ссылка].  \nА теперь давай найдём твои занятия! Жми «Расписание» 👇",reply_markup=keyboards.start_keyboard())    
    # await message.answer(f"Привет, студент! 🎓\nЯ тут, чтобы ты никогда не опоздал на пару (ну, почти никогда).\nЧто могу:\n✓ Показать расписание твоей группы на любой день.\n✓ Найти, где и когда ведёт занятия нужный препод.\n✓ Напомнить о парах (включи уведомления!).\n✓ Данные расписания обновлются автоматически при изменении анализе даты на сайте.\n\nЯ открытый проект — мой код на GitHub: [ссылка].  \nА теперь давай найдём твои занятия! Жми «Расписание» 👇", reply_markup=keyboards.start_keyboard())
        
@privateChatRouter.callback_query(lambda call: call.data == "get_schedule")
async def get_schedule(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption="Для получения расписания нужно выбрать режим работы. Выбери режим вывода:", reply_markup=keyboards.choice_mode_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "today")
async def today(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption="Расписание на сегодня:", reply_markup=keyboards.today_schedule_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "current_day")
async def current_day(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption="Для отображения расписания на определенный день выбери день(автоматически будет определено какая неделя: над чертой или под чертой):", reply_markup=keyboards.current_day_schedule_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "week")
async def week(callback: CallbackQuery) -> None:
    await callback.message.edit_caption(caption="Расписание на неделю:", reply_markup=keyboards.week_schedule_keyboard())