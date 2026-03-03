import datetime
from database.requests import find_teacher
from tables.schedule_manager import WEEK_DAYS
from typing import List

async def format_teacher_week_schedule(teacher_query: str, week_type: int):
    # Очистка запроса (убираем команду, если она есть)
    teacher_name = teacher_query.replace("/find ", "").strip()
    
    header_text = f"🔎 <b>Расписание {teacher_name}</b>\n"
    header_text += f"Неделя: <b>{'I' if week_type == 1 else 'II'}</b>\n"
    
    result_msg = [header_text]
    has_any_lesson = False

    for day_key in WEEK_DAYS:
        day_name = WEEK_DAYS[day_key][0]
        results = await find_teacher(teacher_name, day_name, week_type)
        
        if not results:
            continue
            
        has_any_lesson = True
        
        # 1. Формируем начало блока (заголовок дня будет "лицом" свернутой цитаты)
        day_block = f"<blockquote expandable><b>📅 {day_name.upper()}</b>\n"
        
        # Группировка
        groups_dict = {}
        for i in results:
            key = (i.start_time, i.subject, i.audience)
            if key not in groups_dict:
                groups_dict[key] = []
            if i.group_name not in groups_dict[key]:
                groups_dict[key].append(i.group_name)
        
        # Сортировка по времени
        sorted_keys = sorted(groups_dict.keys(), key=lambda x: list(map(int, x[0].split(':'))))
        
        # 2. Добавляем пары внутрь этого дня
        for (time, subject, audience) in sorted_keys:
            group_list = ", ".join(groups_dict[(time, subject, audience)])
            day_block += f"⏱️ <b>{time}</b> — гр. {group_list}\n📚 {subject}\n📍 Ауд: <b>{audience}</b>\n\n"
        
        # 3. Закрываем блок ОДИН раз
        day_block += "</blockquote>"
        result_msg.append(day_block)
            
    if not has_any_lesson:
        return f"Пар у преподавателя <i>{teacher_name}</i> на неделю {'I' if week_type == 1 else 'II'} не найдено."

    # Соединяем всё, используя один перенос строки между блоками
    return "\n".join(result_msg)