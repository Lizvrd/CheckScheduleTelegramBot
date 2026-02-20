import pandas as pd
import os
import datetime
from typing import Dict, List
import asyncio
from upper_under_schedule_filter import filter, get_upper_under_week_type

WEEK_DAYS = {
    0: ['Понедельник', 2],
    1: ['Вторник', 16],
    2: ['Среда', 30],
    3: ['Четверг',44],
    4: ['Пятница', 58],
    5: ['Суббота', 72]
}

COUNT_LESSONS_DAY = 7

async def save_groups_sheet_in_file(dir: str)->Dict[str, str]:
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

async def filter_columns_group(group: str) -> pd.DataFrame:
    """Фильтрация столбцов по группе
    
    Эта функция находит файл и лист, соответствующие заданной группе,
    затем фильтрует столбцы в зависимости от позиции группы в заголовке.
    
    Args:
        group (str): Название группы для фильтрации
        
    Returns:
        DataFrame: Отфильтрованный DataFrame
    """
    founded_sheet_group = await save_groups_sheet_in_file('schedules/semester/')
    
    file_name = founded_sheet_group[group][0]
    sheet_name = founded_sheet_group[group][1]
    
    df = pd.read_excel(file_name, sheet_name=sheet_name)
    header = founded_sheet_group[group][2]
    
    # Если группа находится в 5-й позиции (индекс 5), выбираем первые 9 столбцов
    # Иначе выбираем столбцы с 10-го по предпоследний
    if header.index(group) == 5:
        df = df.iloc[:, :9]
    else:
        df = df.iloc[:, 10:-2]
    return df
    
async def filter_columns_group_by_date() -> str:
    """Фильтрация столбцов по группе и дате
    
    Args:
        group (str): Название группы для фильтрации
        date (datetime.datetime): Дата для фильтрации
        
    Returns:
        str: Строковое представление отфильтрованного DataFrame
    """
    date = datetime.datetime.now().weekday()
    week_day = WEEK_DAYS[date]
    return week_day[1]

async def message_constructor(schedule: pd.DataFrame) -> str:
    """Construct a message with the schedule information

    Args:
        schedule (pd.DataFrame): Schedule data

    Returns:
        str: Formatted schedule message
    """
    TABLE_LESSONS = ''
    
    # Check if schedule has data
    if schedule.empty:
        return "Нет данных для отображения"
    
    # Iterate over actual number of rows instead of fixed COUNT_LESSONS_DAY
    for i in range(len(schedule)):
        # Check if the row has enough columns before accessing them
        if len(schedule.columns) >= 4:
            try:
                subject = schedule.iloc[i,-4]
                type_lesson = schedule.iloc[i,-3]
                audience = str(schedule.iloc[i,-1]).split(' ')
                
                if len(audience) > 1:
                    audience = audience[2]
                elif len(audience) == 1 and audience[0] == 'nan':
                    continue
                        
                TABLE_LESSONS += f'{i+1}. {subject} ({type_lesson}) {audience}\n'
            except IndexError:
                continue
    
    return TABLE_LESSONS
    

async def get_today_schedule(group: str) -> str:
    """Возвращает расписание на сегодня для заданной группы
    
    Args:
        group (str): Название группы для фильтрации
        
    Returns:
        str: Строковое представление расписания на сегодня
    """
    date_today = await filter_columns_group_by_date()
    if date_today == 'Воскресенье':
        return "Сегодня выходной. Занятия не проводятся :)"
    else:
        schedule_today = await filter_columns_group(group)
        schedule_today = schedule_today.iloc[date_today:date_today+14]
        schedule_today = await filter(df=schedule_today)
    
    return await message_constructor(schedule_today)
    

async def get_tomorrow_schedule(group) -> str:
    date = datetime.datetime.now().weekday()
    try:
        date_tomorrow = date + 1
        if date_tomorrow == 6:
            return "Завтра выходной. Занятия не проводятся :)"
        elif date_tomorrow == 7:
            date_tomorrow = 0
        
        schedule_tomorrow = await filter_columns_group(group)
        schedule_tomorrow = schedule_tomorrow.iloc[date_tomorrow:date_tomorrow+14]
        schedule_tomorrow = await filter(df=schedule_tomorrow)
    
        return await message_constructor(schedule_tomorrow)
    except KeyError:
        return "Завтра выходной. Занятия не проводятся :)"

async def get_week_schedule(group) -> str:
    date_name = list(WEEK_DAYS.keys())
    result = ""
    for i in date_name:
        day = WEEK_DAYS[i][0]
        day_schedule = WEEK_DAYS[i][1]
        # Check if next day exists to avoid KeyError
        if i+1 in WEEK_DAYS:
            next_day = WEEK_DAYS[i+1]
            if next_day == 6:
                schedule_week = await filter_columns_group(group)
                schedule_week = schedule_week.iloc[day_schedule:]
                schedule_week = await filter(df=schedule_week)
            else:    
                schedule_week = await filter_columns_group(group)
                schedule_week = schedule_week.iloc[day_schedule:next_day[1]]
                schedule_week = await filter(df=schedule_week)
        else:
            # Handle the case when there's no next day (Saturday)
            schedule_week = await filter_columns_group(group)
            schedule_week = schedule_week.iloc[day_schedule:]
            schedule_week = await filter(df=schedule_week)
        result += f'{day}\n{await message_constructor(schedule_week)}\n'
    return result

    
async def main():
    print(await get_today_schedule('Б24-281-1'))
    print(await get_tomorrow_schedule('Б24-281-1'))
    print(await get_week_schedule('Б24-281-1'))

if __name__ == '__main__':
    asyncio.run(main())