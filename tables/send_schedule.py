import pandas as pd
import re
import datetime
from .schedule_manager import filter_columns_group, filter_columns_group_by_date, WEEK_DAYS
from .upper_under_schedule_filter import filter as week_filter

async def message_constructor(schedule: pd.DataFrame) -> str:
    if schedule.empty:
        return ""

    table_lessons = []
    processed_keys = set()

    for i in range(len(schedule)):
        row = schedule.iloc[i]
        try:
            # Вычисляем номер пары: от 1 до 7
            # Индексы: 2,3->1 пара; 4,5->2 пара ... 14,15->7 пара
            original_idx = row.name
            lesson_num = str(((original_idx - 2) % 14) // 2 + 1)

            subject_raw = str(row.iloc[-4]).replace('\n', ' ').strip()
            type_raw = str(row.iloc[-3]).replace('\n', ' ').strip()
            aud_raw = str(row.iloc[-1]).replace('\n', ' ').strip()

            # Пропускаем пустые ячейки
            if subject_raw.lower() in ['nan', '', '-', 'none']:
                continue

            # Очистка названия и типа
            subject = " ".join(dict.fromkeys(subject_raw.replace('.', ' ').split()))
            l_type = " ".join(dict.fromkeys(type_raw.replace('(', '').replace(')', '').split()))

            # Аудитория
            match = re.search(r'(\d+-[А-Яа-яA-Za-z0-9-]+)|(корп\.\d+)', aud_raw)
            audience = match.group(0) if match else aud_raw.replace('nan', '').strip()

            # Сборка
            type_str = f"({l_type})" if l_type else ""
            aud_str = f" {audience}" if audience else ""
            line = f"{lesson_num}. {subject} {type_str}{aud_str}"
            line = " ".join(line.split())

            # Защита от дублей (на случай если фильтр пропустил лишнюю строку)
            key = f"{lesson_num}_{subject}"
            if key not in processed_keys:
                table_lessons.append(line)
                processed_keys.add(key)
        except:
            continue

    return "\n".join(table_lessons)

async def get_today_schedule(group: str) -> str:
    # Используем твою функцию получения индекса
    date_info = await filter_columns_group_by_date()
    _date_today_idx = int(date_info[0])
    
    if _date_today_idx > 86: # Воскресенье или за пределами
        return "Сегодня выходной. Занятия не проводятся :)"

    df = await filter_columns_group(group)
    # Берем блок строк на 1 день (обычно 14 строк для I/II недель)
    day_df = df.iloc[_date_today_idx : _date_today_idx + 14]
    day_df = await week_filter(day_df)
    
    result = await message_constructor(day_df)
    return result if result else "Сегодня выходной. Занятия не проводятся :)"

async def get_tomorrow_schedule(group: str) -> str:
    """Расписание на завтра"""
    # 0 - пн, 6 - вс
    now = datetime.datetime.now()
    tomorrow_weekday = (now.weekday() + 1) % 7
    
    if tomorrow_weekday == 6:
        return "Завтра воскресенье. Занятия не проводятся :)"

    # Находим индекс строки для завтрашнего дня в WEEK_DAYS
    day_info = WEEK_DAYS.get(tomorrow_weekday)
    if not day_info:
        return "На завтра расписание не найдено :("
        
    start_row = day_info[1]
    df = await filter_columns_group(group)
    
    # Срез на завтра
    day_df = df.iloc[start_row : start_row + 14]
    
    # Применяем фильтр недели
    # Примечание: если сегодня воскресенье, week_filter уже поймет, 
    # что идет текущая календарная неделя (ISO)
    day_df = await week_filter(day_df)
    
    result = await message_constructor(day_df)
    return result if result else "Завтра выходной. Занятия не проводятся :)"

async def get_week_schedule(group: str) -> str:
    result = []
    for day_idx, day_info in WEEK_DAYS.items():
        day_name = day_info[0]
        start_row = day_info[1]
        
        if day_idx < 5:
            end_row = WEEK_DAYS[day_idx + 1][1]
        else:
            end_row = start_row + 14

        df = await filter_columns_group(group)
        day_df = df.iloc[start_row:end_row]
        day_df = await week_filter(day_df)
        
        day_schedule = await message_constructor(day_df)
        
        if not day_schedule:
            result.append(f"{day_name}\nВыходной. Занятия не проводятся :)\n")
        else:
            result.append(f"{day_name}\n{day_schedule}\n")
            
    return "\n".join(result)