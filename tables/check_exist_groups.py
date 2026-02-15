from .get_all_exist_group import get_all_exist_groups
import pandas as pd

async def check_exist_groups(user_text: str) -> bool:
    """## Функция для проверки написанного сообщения пользователя(группы)
    на правильность и существования
    
    ### Почему программа работает с schedule/exams?:
    Дело в том, что если рассматривать файлы с экзаменами, то в них группы(по курсам) идут по порядку в колонке
    Такие данные проще всего получить чем в файлах с расписанием, где номер группы идет вместе с:
    * Типом расписания (над или под чертой)
    * Предмет
    * Преподаватель
    * Номер аудитории (ссылка)
    
    Args:
        user_text (str): message.text, который отправляет пользователь

    Returns:
        bool: Возвращает True, если пользователь написал правильно и существует, иначе False
    """
    
    exist_groups = await get_all_exist_groups(dir='schedules/exams')
    if user_text.upper() in exist_groups:
        return True
    else:
        return False