import datetime
from database.requests import find_teacher
from tables.schedule_manager import WEEK_DAYS
from typing import List

async def format_teacher_schedule(message):
    args = message.split(maxsplit=1)
    if len(args) < 2:
        return("Пожалуйста, укажите фамилию как на примере <code>/find Фамилия</code>")
        
    teacher_query = args[1].strip()
    now = datetime.datetime.now()
    current_week = 1 if now.isocalendar()[1] % 2 == 0 else 2
    day_name = WEEK_DAYS[now.weekday()][0] if now.weekday() < 6 else "Понедельник"

    results = await find_teacher(teacher_query, day_name, current_week)
    
    if not results:
        return f"На сегодня пар у преподавателя <i>{teacher_query}</i> не найдено"

    # Группировка потоковых лекций
    groups_dict = {}
    for i in results:
        # В ключ добавляем еще и название предмета, чтобы разные пары в одно время не слились
        key = (i.start_time, i.subject, i.audience)
        if key not in groups_dict:
            groups_dict[key] = []
        if i.group_name not in groups_dict[key]:
            groups_dict[key].append(i.group_name)
        
    result_msg = [f"🔎 <b>Расписание {teacher_query} на сегодня:</b>\n"]
    
    # Сортируем по времени
    sorted_keys = sorted(groups_dict.keys(), key=lambda x: list(map(int, x[0].split(':'))))
    
    for (time, subject, audience) in sorted_keys:
        group_list = ", ".join(groups_dict[(time, subject, audience)])
        result_msg.append(f"⏱️ <b>{time}</b> — гр. {group_list}")
        result_msg.append(f"📚 {subject}")
        result_msg.append(f"📍 Ауд: <b>{audience}</b>\n")
        
    return ("\n".join(result_msg))