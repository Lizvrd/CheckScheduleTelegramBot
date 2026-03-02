from database.requests import get_users_for_notifications, get_lesson_for_notification
import asyncio
from configBot import bot
from tables.send_schedule import get_today_schedule, get_tomorrow_schedule
from datetime import datetime, timedelta
from tables.schedule_manager import WEEK_DAYS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Отправка уведомления утром(утренний отчет)
async def send_morning_today_report():
    day_now = datetime.now().weekday()
    day_now = WEEK_DAYS[day_now][0] #Берем название дня недели исходя из словаря 
    if not day_now:
        return
    
    users_data = await get_users_for_notifications()
    for settings, group in users_data:
        if settings.morning_summary and group:
            try:
                schedule_text = await get_today_schedule(group=group)
                if "Сегодня выходной. Занятия не проводятся :)":
                    await bot.send_message(chat_id=settings.telegram_id, text=f"🦊 Доброе утро! Квант проснулся раньше тебя и проанализировал расписание на сегодня. Вот что я раскопал:\n\n{schedule_text}")
                    await asyncio.sleep(0.05)
            except Exception as e:
                print(f'{settings.telegram_id}: {e}')

# Составление плана пар на завтра(вечерний отчет)       
async def send_evening_report():
    day_now = datetime.now().weekday()
    if day_now == 6:
        day_now = WEEK_DAYS[day_now%6][0] #Берем название дня недели исходя из словаря 
    
    users_data = await get_users_for_notifications()
    for row in users_data:
        settings = row[0]
        group = row[1]
        if settings.evening_summary and group:
            try:
                schedule_text = await get_tomorrow_schedule(group=group)
                if "Завтра выходной. Занятия не проводятся :)":
                    await bot.send_message(chat_id=settings.telegram_id, text=f"🦊 Снова привет! Я подготовил для тебя план пар на завтра, как ты и просил:\n\n{schedule_text}")
                    await asyncio.sleep(0.05)
            except Exception as e:
                print(f'{settings.telegram_id}: {e}')
        else:
            print(f"Юзер {settings.telegram_id} был пропущен")
            
async def notify_about_soon_subject():
    """Проверяет, есть ли у кого-то пара через N минут"""
    now = datetime.now()
    # Определяем текущую неделю (1 или 2)
    curr_week = 1 if datetime.isocalendar(now)[1] % 2 != 0 else 2
    day_name = WEEK_DAYS[now.weekday()-1][0] if now.weekday() == 6 else WEEK_DAYS[now.weekday()][0]
    
    users = await get_users_for_notifications()
    for settings, group in users:
        # Время пары = сейчас + оффсет (30, 60 и т.д.)
        target_time_obj = now + timedelta(minutes=settings.time_offset)
        target_time_str = target_time_obj.strftime("%H:%M")
        lesson = await get_lesson_for_notification(group=group, day=day_name, week_type=curr_week, time_str=target_time_str)
        if lesson:
            await bot.send_message(settings.telegram_id, f"🔔 Через {settings.time_offset} мин начнется пара: {lesson.subject} (ауд. {lesson.audience})")
    
# сетап всех уведомлений по времени 
async def setup_scheduler():
    scheduler = AsyncIOScheduler(timezone="Europe/Samara")
    scheduler.add_job(send_morning_today_report, 'cron', hour=7, minute=30)
    scheduler.add_job(send_evening_report, 'cron',hour=20,minute=00)
    scheduler.add_job(notify_about_soon_subject, 'interval', minutes=1)
    
    from tables.schedule_manager import rebuild_all_lessons_cache
    scheduler.add_job(rebuild_all_lessons_cache, 'cron', day_of_week='sun', hour=15, minute=0)
    
    scheduler.start()
    print("Планировщик запущен (UTC+4)\n🦊 Квант вышел на дежурство")