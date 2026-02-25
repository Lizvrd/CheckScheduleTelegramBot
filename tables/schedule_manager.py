import pandas as pd
import os
import datetime
from typing import Dict, List
import asyncio
from .upper_under_schedule_filter import filter

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
            df = df.iloc[:, 10:-2]
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