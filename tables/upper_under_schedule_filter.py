import pandas as pd
import os
import requests
from bs4 import BeautifulSoup as soup
from dotenv import load_dotenv
import asyncio

load_dotenv()
async def get_upper_under_week_type(url: str) -> str:
    response = requests.get(url)
    page_soup = soup(response.text, 'html.parser')
    upper_under_week_type = page_soup.find('div', {'class': 'site-header-top-element ref-week type-separated'}).text
    return upper_under_week_type


async def filter(url: str): 
    testWork = pd.read_excel(os.path.join('schedules/semester/Расписание%20занятий%20П,%20оч.%20форма%20обучения,%20весенний%20семестр%202025-2026%20уч.г..xlsx'),sheet_name='11')
    # print(testWork['Unnamed: 4'])
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        filtred  = testWork['Unnamed: 4'] == 'II' if await get_upper_under_week_type(url) == 'Неделя под чертой' else testWork['Unnamed: 4'] == 'I'
        result = testWork[filtred]
        with open('test.txt', 'w', encoding='utf-8') as f:
            f.write(result.to_string())


async def main():
    url = os.getenv('WEBSITE_URL')
    upper_under_week_type = await filter(url)
    print(upper_under_week_type)

if __name__ == '__main__':
    asyncio.run(main())