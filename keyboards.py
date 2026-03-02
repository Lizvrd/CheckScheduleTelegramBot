from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Расписание", callback_data="get_schedule")],
        [InlineKeyboardButton(text="Настройки", callback_data="settings")]
    ])    

def choice_mode_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Расписание на сегодня", callback_data="today")],
        [InlineKeyboardButton(text="Расписание на завтра", callback_data="tomorrow")],
        [InlineKeyboardButton(text="Расписание на неделю", callback_data="week")]
    ])

def schedule_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться", callback_data="get_schedule")]
    ])
    
def settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Уведомления", callback_data="notification_mode")],
        # [InlineKeyboardButton(text="Выбрать язык", callback_data="language_mode")],
        [InlineKeyboardButton(text="Вернуться", callback_data="get_schedule")],
    ])

def notify_settings(is_active, time_offset, morning, evening):
    # Формируем текст для кнопок на основе данных из БД
    main_btn_text = "✅ Уведомления: Активны" if is_active else "❌ Уведомления: Выключены"
    morning_emoji = "✅" if morning else "❌"
    evening_emoji = "✅" if evening else "❌"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=main_btn_text, callback_data="notif_main_toggle")],
        [InlineKeyboardButton(text=f"⏰ Напомнить за: {time_offset} мин", callback_data="notif_time_cycle")],
        [InlineKeyboardButton(text=f"🌅 Сводка на день: {morning_emoji}", callback_data="notif_morning_toggle")],
        [InlineKeyboardButton(text=f"🌃 План на завтра: {evening_emoji}", callback_data="notif_evening_toggle")],
        [InlineKeyboardButton(text="🔙 Назад в настройки", callback_data="settings")]
    ])