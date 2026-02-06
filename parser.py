import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

async def check_current_date(url : str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    schedule_data = soup.find('div', class_='wall-content-inner')
    current_date = schedule_data.find('span').text
    return current_date