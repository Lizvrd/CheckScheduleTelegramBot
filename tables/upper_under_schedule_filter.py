import pandas as pd
import os
import requests
from bs4 import BeautifulSoup as soup
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def get_upper_under_week_type(url) -> str:
    response = requests.get(url)
    page_soup = soup(response.text, 'html.parser')
    upper_under_week_type = page_soup.find('div', {'class': 'site-header-top-element ref-week type-separated'}).text
    return upper_under_week_type


async def filter(df: pd.DataFrame): 
    # Работаем непосредственно с DataFrame, а не читаем его из файла
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        # Используем правильный способ фильтрации DataFrame
        week_type = await get_upper_under_week_type(url=os.getenv('WEBSITE_URL'))
        
        # Фильтруем по типу недели (I или II)
        if week_type == 'Неделя под чертой':
            # Для недели под чертой фильтруем по значению 'II'
            filtered = df[df.iloc[:, 4] == 'II'] if len(df.columns) > 4 else df
        else:
            # Для обычной недели фильтруем по значению 'I'
            filtered = df[df.iloc[:, 4] == 'I'] if len(df.columns) > 4 else df
            
        return filtered