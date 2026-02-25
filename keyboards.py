from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Расписание", callback_data="get_schedule")],
        [InlineKeyboardButton(text="О проекте", callback_data="about_project", url="https://example.com")]
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