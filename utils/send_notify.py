from database.requests import get_users_for_notifications
import asyncio
from configBot import bot
from tables.send_schedule import get_today_schedule, get_tomorrow_schedule
from datetime import datetime, timedelta
from tables.schedule_manager import WEEK_DAYS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
            
async def setup_scheduler():
    scheduler = AsyncIOScheduler(timezone="Europe/Samara")
    scheduler.add_job(send_morning_today_report, 'cron', hour=7, minute=30)
    scheduler.add_job(send_evening_report, 'cron',hour=20,minute=00)
    
    scheduler.start()
    print("Планировщик запущен (UTC+4)\n🦊 Квант вышел на дежурство")