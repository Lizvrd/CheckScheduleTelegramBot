import pandas as pd
from .schedule_manager import filter_columns_group, filter_columns_group_by_date, WEEK_DAYS
from .upper_under_schedule_filter import get_upper_under_week_type

async def message_constructor(schedule: pd.DataFrame) -> str:
    """Construct a message with the schedule information

    Args:
        schedule (pd.DataFrame): Schedule data

    Returns:
        str: Formatted schedule message
    """
    TABLE_LESSONS = ''
    
    # Handle empty DataFrames
    if schedule.empty:
        return "Нет занятий"
    
    # Import the filter function to determine current week type
    week_type = get_upper_under_week_type()
    is_odd_week = week_type % 2 != 0  # True for 'II' week, False for 'I' week
    
    # Process each row in the DataFrame
    # We need to handle pairs of rows (one for each week type)
    i = 0
    lesson_number = 1
    while i < len(schedule):
        try:
            # Check if we have enough columns
            if len(schedule.columns) >= 3:
                # For pairs of rows, we take the one that matches the current week type
                # Row i is for 'I' week, row i+1 is for 'II' week
                if is_odd_week:  # 'II' week
                    # Take row i+1 if it exists, otherwise row i
                    row_index = i + 1 if i + 1 < len(schedule) else i
                else:  # 'I' week
                    # Take row i
                    row_index = i
                
                subject = schedule.iloc[row_index, -3] if len(schedule.columns) >= 3 and not pd.isna(schedule.iloc[row_index, -3]) else ""
                type_lesson = schedule.iloc[row_index, -2] if len(schedule.columns) >= 2 and not pd.isna(schedule.iloc[row_index, -2]) else ""
                audience_raw = schedule.iloc[row_index, -1] if len(schedule.columns) >= 1 and not pd.isna(schedule.iloc[row_index, -1]) else ""
                
                # Skip if subject is empty
                if not subject or pd.isna(subject) or str(subject).strip() == "":
                    i += 2  # Skip both rows in the pair
                    lesson_number += 1  # Still increment lesson number to maintain proper numbering
                    continue
                    
                # Process audience information
                audience_parts = str(audience_raw).split(' ')
                audience = ""
                if len(audience_parts) > 2:
                    audience = audience_parts[2]
                elif len(audience_parts) == 1 and audience_parts[0] != 'nan':
                    audience = audience_parts[0]
                    
                # Only add to lessons if we have subject information
                if subject and str(subject).strip() != "NaN" and str(subject).strip() != "nan":
                    TABLE_LESSONS += f'{lesson_number}. {subject} ({type_lesson}) {audience}\n'
                # Always increment lesson number to maintain proper numbering
                lesson_number += 1
                    
                i += 2  # Move to the next pair of rows
            else:
                # Handle DataFrames with fewer than 3 columns
                if len(schedule.columns) >= 1:
                    subject = schedule.iloc[i, -1] if not pd.isna(schedule.iloc[i, -1]) else ""
                    if subject and str(subject).strip() != "" and str(subject).strip() != "NaN" and str(subject).strip() != "nan":
                        TABLE_LESSONS += f'{lesson_number}. {subject}\n'
                    lesson_number += 1
                i += 1
        except IndexError:
            # Skip rows that cause index errors
            i += 1 if len(schedule.columns) < 3 else 2
            lesson_number += 1
            continue
        except Exception:
            # Skip rows with any other errors
            i += 1 if len(schedule.columns) < 3 else 2
            lesson_number += 1
            continue
            
    return TABLE_LESSONS if TABLE_LESSONS else "Нет занятий"

async def get_today_schedule(group: str) -> str:
    """Возвращает расписание на сегодня для заданной группы
    
    Args:
        group (str): Название группы для фильтрации
        
    Returns:
        str: Строковое представление расписания на сегодня
    """
    date_list = await filter_columns_group_by_date()
    _date_today = int(date_list[0])
    if _date_today > 86:
        return "Сегодня выходной. Занятия не проводятся :)"

    schedule_today = await filter_columns_group(group)
    # Slice by date first, then apply week filter
    # Make sure we don't go out of bounds
    if _date_today < len(schedule_today):
        end_index = min(_date_today + 14, len(schedule_today))
        schedule_today = schedule_today.iloc[_date_today:end_index]
    else:
        schedule_today = schedule_today.iloc[0:0]  # Empty DataFrame

    return await message_constructor(schedule_today)

async def get_tomorrow_schedule(group) -> str:
    """Возвращает расписание на завтра для заданной группы
    
    Args:
        group (str): Название группы для фильтрации
        
    Returns:
        str: Строковое представление расписания на завтра
    """
    date_now = await filter_columns_group_by_date()
    _date_tomorrow = int(date_now[1]) + 1
    if _date_tomorrow == 6:
        return "Завтра выходной. Занятия не проводятся :)"
    elif _date_tomorrow == 7:
        _date_tomorrow = 0
    
    schedule_tomorrow = await filter_columns_group(group)
    # Slice by date first, then apply week filter
    day_start = WEEK_DAYS[_date_tomorrow][1]
    # Make sure we don't go out of bounds
    if day_start < len(schedule_tomorrow):
        end_index = min(day_start + 14, len(schedule_tomorrow))
        schedule_tomorrow = schedule_tomorrow.iloc[day_start:end_index]
    else:
        schedule_tomorrow = schedule_tomorrow.iloc[0:0]  # Empty DataFrame

    return await message_constructor(schedule_tomorrow)
    
async def get_week_schedule(group) -> str:
    """Возвращает расписание на неделю для заданной группы
    
    Args:
        group (str): Название группы для фильтрации
        
    Returns:
        str: Строковое представление расписания на неделю
    """
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
                # Slice by date first, then apply week filter
                # Make sure we don't go out of bounds
                if day_schedule < len(schedule_week):
                    schedule_week = schedule_week.iloc[day_schedule:]
                else:
                    schedule_week = schedule_week.iloc[0:0]  # Empty DataFrame
                # schedule_week = await filter(df=schedule_week)
            else:
                schedule_week = await filter_columns_group(group)
                # Slice by date first, then apply week filter
                # Make sure we don't go out of bounds
                if day_schedule < len(schedule_week):
                    end_index = min(next_day[1], len(schedule_week))
                    schedule_week = schedule_week.iloc[day_schedule:end_index]
                else:
                    schedule_week = schedule_week.iloc[0:0]  # Empty DataFrame
                # schedule_week = await filter(df=schedule_week)
        else:
            # Handle the case when there's no next day (Saturday)
            schedule_week = await filter_columns_group(group)
            # Slice by date first, then apply week filter
            # Make sure we don't go out of bounds
            if day_schedule < len(schedule_week):
                schedule_week = schedule_week.iloc[day_schedule:]
            else:
                schedule_week = schedule_week.iloc[0:0]  # Empty DataFrame
            # schedule_week = await filter(df=schedule_week)
        result += f'{day}\n{await message_constructor(schedule_week)}\n'
    return result