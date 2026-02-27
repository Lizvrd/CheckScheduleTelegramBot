from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F
from configBot import bot
import keyboards
from dotenv import load_dotenv
import os
from aiogram.fsm.context import FSMContext
from tables.check_exist_groups import check_exist_groups
from tables.send_schedule import get_today_schedule, get_tomorrow_schedule, get_week_schedule
from database.requests import set_user, update_user_group, get_user_group, get_cached_schedule

load_dotenv()

privateChatRouter = Router()

@privateChatRouter.message(CommandStart())
async def startChat(message: Message) -> None:

    user = await get_user_group(message.from_user.id)
    if user:
        await bot.send_photo(message.from_user.id, photo=os.getenv("SAY_HELLO_PHOTO_LINK"), caption=f"🦊Привет, студент!\nРад снова тебя видеть .\nТвоя сохраненная группа: <i>{user}</i>.\n\nЕсли ты хочешь изменить свою группу, напиши новое название группы.\n\nПримеры: Б12-345-6\nб12-345-6", reply_markup=keyboards.start_keyboard())
        return
    
    await bot.send_photo(message.from_user.id, photo=os.getenv("SAY_HELLO_PHOTO_LINK"), caption=f"🦊Привет, студент!\n\nЧтобы начать работу с ботом, напиши свою группу.\nПримеры: Б12-345-6\nб12-345-6")

@privateChatRouter.message(F.text)
async def save_group(message: Message) -> None:    
    user_text = message.text

    if await check_exist_groups(user_text=user_text) == False:
        await bot.send_photo(message.from_user.id, photo=os.getenv("NOT_FOUND_GROUP_LINK"), caption=f"🦊Группа <i>{user_text}</i> не найдена. Возможно, что вы ввели неправильное название группы.\nПроверьте правильность ввода.\nПримеры: Б12-345-6\nб12-345-6")
        return

    await set_user(tg_id=message.from_user.id, username=message.from_user.username)
    await update_user_group(tg_id=message.from_user.id, group=user_text)
    
    await bot.send_photo(message.from_user.id, photo=os.getenv("GROUP_IS_FOUND_LINK"), caption=f"🦊Привет, студент! 🎓\nЯ тут, чтобы ты никогда не опоздал на пару (ну, почти никогда).\nЧто могу:\n✓ Показать расписание твоей группы на любой день.\n✓ Найти, где и когда ведёт занятия нужный препод.\n✓ Напомнить о парах (включи уведомления!).\n✓ Данные расписания обновлются автоматически при изменении анализе даты на сайте.\n\nА теперь давай найдём твои занятия! Жми «Расписание» 👇",reply_markup=keyboards.start_keyboard())

@privateChatRouter.callback_query(lambda call: call.data == "get_schedule")
async def get_schedule(callback: CallbackQuery) -> None:
    await callback.message.edit_media(media=InputMediaPhoto(media=os.getenv("GROUP_IS_FOUND_LINK"),caption="🦊Для получения расписания нужно выбрать режим работы. Выбери режим вывода:"), reply_markup=keyboards.choice_mode_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "today")
async def send_today_schedule(callback: CallbackQuery) -> None:
    group = await get_user_group(tg_id=callback.from_user.id)
    
    if not group:
        await callback.answer(text="Сначала введите группу в чат")
        return
    
    await callback.message.edit_media(media=InputMediaPhoto(media=os.getenv("TODAY_SCHEDULE_LINK"),caption=f"🦊Расписание на сегодня: \n{await get_today_schedule(group=group)}"),reply_markup=keyboards.schedule_keyboard())

@privateChatRouter.callback_query(lambda call: call.data == "tomorrow")
async def send_tomorrow_schedule(callback: CallbackQuery) -> None:
    group = await get_user_group(tg_id=callback.from_user.id)

    if not group:
        await callback.answer(text="Сначала введите группу в чат")
        return

    await callback.message.edit_media(media=InputMediaPhoto(media=os.getenv("TOMORROW_SCHEDULE_LINK"),caption=f"🦊Расписание на завтра: \n{await get_tomorrow_schedule(group=group)}"),reply_markup=keyboards.schedule_keyboard())
    
@privateChatRouter.callback_query(lambda call: call.data == "week")
async def send_week_schedule(callback: CallbackQuery) -> None:
    group = await get_user_group(tg_id=callback.from_user.id)

    schedule_text = await get_cached_schedule(group=group)
    if not group:
        await callback.message.answer(text="Сначала введите группу в чат")
        return
    if len(schedule_text) > 1024:
        await callback.message.delete()
        await callback.message.answer(text=schedule_text, reply_markup=keyboards.schedule_keyboard())
    await callback.message.edit_media(media=InputMediaPhoto(media=os.getenv("WEEK_SCHEDULE_LINK"),caption=f"🦊Расписание на неделю: \n{schedule_text}"),reply_markup=keyboards.schedule_keyboard())

@privateChatRouter.callback_query(lambda call: call.data == "settings")
async def show_settings(callback: CallbackQuery):
    await callback.message.edit_media(media=InputMediaPhoto(media=os.getenv('SETTINGS'),caption="Вы находитесь в настройках бота. Выберите что хотите изменить"), reply_markup=keyboards.settings_keyboard())
  
@privateChatRouter.callback_query(lambda call: call.data == "notification_mode")
async def notification_mode(callback: CallbackQuery):
    await callback.message.answer(text="Настройки уведомленийn\n\nСписок настроек:\n", reply_markup=keyboards.notify_settings())