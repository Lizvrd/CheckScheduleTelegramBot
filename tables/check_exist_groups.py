from .schedule_manager import save_groups_sheet_in_file
import pandas as pd

async def check_exist_groups(user_text: str) -> bool:
    """## Функция для проверки написанного сообщения пользователя(группы)
    на правильность и существования
    
    ### Почему программа работает с schedule/semester?:
    В дальнейшем парсинге таблиц будем использоваться директория schedules/semester,
    так как в ней содержатся таблицы с расписанием для всех групп.
    Также в таблице будут содержаться следующие данные:
    * Номер пары
    * Типом расписания (над или под чертой)
    * Предмет
    * Преподаватель
    * Номер аудитории (ссылка)
    
    Args:
        user_text (str): message.text, который отправляет пользователь

    Returns:
        bool: Возвращает True, если пользователь написал правильно и существует, иначе False
    """
    
    exist_groups = await save_groups_sheet_in_file(dir='schedules/semester')
    if user_text.upper() in list(exist_groups.keys()):
        return True
    else:
        return False