
import pandas as pd
import os
import datetime
from typing import Dict, List
import asyncio
from .upper_under_schedule_filter import filter
from database.requests import *
WEEK_DAYS = {
    0: ['Понедельник', 2],
    1: ['Вторник', 16],
    2: ['Среда', 30],
    3: ['Четверг',44],
    4: ['Пятница', 58],
    5: ['Суббота', 72]
}

COUNT_LESSONS_DAY = 7


def save_groups_sheets_from_file(dir: str)->Dict[str, str]:
    """Сохранение путей к файлу и листа по названию группы в шапке документа
    Args:
        dir (str): директория с файлами. по дефолту schedules/semester

    Returns:
        Dict[str, str]: словарь с ключами - названиями групп, значениями - пути к файлу и листу в файле
    """
    groups = {}
    
    # Проходим по всем файлам в директории
    for root, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                # Читаем все листы в файле
                all_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
                
                # Проходим по каждому листу
                for sheet_name, df in all_sheets.items():
                    # Проверяем, что в датафрейме есть хотя бы две строки
                    if len(df) >= 2:
                        # Получаем вторую строку (индекс 1)
                        second_row = df.iloc[1]
                        
                        # Добавляем все значения из второй строки в список групп
                        for item in second_row:
                            if pd.notna(item):  # Проверяем, что значение не NaN
                                # Преобразуем в строку и убираем лишние пробелы
                                group_name = str(item).strip()
                                if len(group_name) == 9 and group_name[0] in ['Б','М','С'] and group_name not in groups:  # Проверяем, что строка не пустая
                                    groups[group_name] = [file_path, sheet_name, second_row.to_list()]
                                else:
                                    continue
                                
            except Exception as e:
                print(f"Ошибка при чтении файла {file_path}: {e}")
                continue
    
    return groups

async def update_groups_cache():
    """Обновление кэша групп
    
    Эта функция обновляет глобальную переменную groups,
    вызывая save_groups_sheets_from_file в отдельном потоке.
    
    Returns:
        Dict: Обновленный словарь групп
    """
    global groups
    groups = await asyncio.to_thread(save_groups_sheets_from_file, 'schedules/semester/')
    return groups

async def filter_columns_group(group: str) -> pd.DataFrame:
    """Фильтрация столбцов по группе
    
    Эта функция находит файл и лист, соответствующие заданной группе,
    затем фильтрует столбцы в зависимости от позиции группы в заголовке.
    
    Args:
        group (str): Название группы для фильтрации
        
    Returns:
        DataFrame: Отфильтрованный DataFrame
    """
    founded_sheet_group = await update_groups_cache()
    founded_sheet_group = founded_sheet_group[group]
    file_name = founded_sheet_group[0]
    sheet_name = founded_sheet_group[1]
    
    df = pd.read_excel(file_name, sheet_name=sheet_name)
    header = list(founded_sheet_group[2])
    # Если группа находится в 5-й позиции (индекс 5), выбираем первые 9 столбцов
    # Иначе выбираем столбцы с 10-го по предпоследний
    if header.index(group) == 5:
        # Проверяем, что в DataFrame достаточно столбцов
        if len(df.columns) >= 9:
            df = df.iloc[:, :9]
        else:
            # Если столбцов меньше 9, берем все столбцы
            df = df.iloc[:, :]
    else:
        # Проверяем, что в DataFrame достаточно столбцов для среза [10:-2]
        if len(df.columns) > 10:
            df = df.iloc[:, 10:-1]
        elif len(df.columns) > 0:
            # Если столбцов меньше или равно 10, но больше 0, берем все столбцы
            df = df.iloc[:, :]
        # Если нет столбцов, возвращаем пустой DataFrame
    return df
     
async def filter_columns_group_by_date() -> List[str | int]:
    """Получение информации о дне недели
    
    Эта функция возвращает информацию о текущем дне недели
    и соответствующем ему индексе в расписании.
        
    Returns:
        List[str | int]: Список, содержащий индекс дня в расписании и номер дня недели
    """
    date = datetime.datetime.now().weekday()
    week_day = list(WEEK_DAYS[date])
    return [week_day[1], date]

async def migrate_data_to_db():
    from .send_schedule import get_week_schedule
    if not await is_cache_empty():
        print("Расписание уже сохранено в базу данных")
        return

    groups_dict = await update_groups_cache()
    print("Начало сохранения данных в базу данных")
    for group_name in groups_dict.keys():
        try:
            week_text = await get_week_schedule(group_name)
            await save_cached_schedule(group_name, week_text)
        except Exception as e:
            print(f"Ошибка при сохранении данных для группы {group_name}: {e}")
    print("Сохранение данных в базу данных завершено")
    
# Полностью замени функцию rebuild_all_lessons_cache

async def rebuild_all_lessons_cache():
    from database.requests import clean_all_schedules, save_cached_schedule, add_lesson_to_db
    from .send_schedule import message_constructor, filter_columns_group, get_week_schedule
    from .upper_under_schedule_filter import filter as week_filter
    import datetime
    
    await clean_all_schedules()
    groups_dict = await update_groups_cache() 
    
    now = datetime.datetime.now()
    
    # ЖЕСТКАЯ ЛОГИКА:
    # Если сегодня ВС (6), берем +1 день (ПН).
    # В остальные дни (даже ПН) берем текущую неделю.
    if now.weekday() == 6:
        target_date = now + datetime.timedelta(days=1)
    else:
        target_date = now
    
    target_week_num = target_date.isocalendar()[1]
    target_week_type = 1 if target_week_num % 2 != 0 else 2
    
    print(f"--- ОБНОВЛЕНИЕ ---")
    print(f"Сегодня: {now.strftime('%A')}, Неделя года: {now.isocalendar()[1]}")
    print(f"Целевая неделя для кэша: {target_week_num} (Тип {target_week_type})")
    
    for group_name in groups_dict.keys():
        try:
            # ТУТ СЕКРЕТ: Мы ПРИНУДИТЕЛЬНО передаем target_week_type
            week_text = await get_week_schedule(group_name, week_type=target_week_type)
            await save_cached_schedule(group_name, week_text)
            
            # В Lesson пишем всё
            df = await filter_columns_group(group_name)
            for day_idx, day_info in WEEK_DAYS.items():
                day_df = df.iloc[day_info[1] : day_info[1] + 14]
                for w_type in [1, 2]:
                    f_df = await week_filter(day_df, week_type=w_type)
                    await message_constructor(f_df, save_to_db=True, group=group_name, day=day_info[0], week_type=w_type)
        except Exception as e:
            print(f"Ошибка {group_name}: {e}")