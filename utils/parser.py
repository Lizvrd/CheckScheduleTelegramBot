import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List
from urllib.parse import urljoin
import os

load_dotenv()
def check_current_date(url : str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    schedule_data = soup.find('div', class_='wall-content-inner')
    current_date = schedule_data.find('span').text
    return current_date

def get_list_facultetes(url: str) -> List[str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    list_facultetes = soup.find('tbody').text
    lsit = list_facultetes.split('\n')
    already_list = []
    for item in lsit:
        if ((len(item) in range(1, 5)) or ('филиал' in item)) and (item != '\xa0'):
            already_list.append(item)
    return already_list

def get_set_xlsx_links(url: str)->List:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    files_links = soup.find_all('a', href=True)
    xlsx_file_links = []
    
    for file in files_links:
        href = file['href']
        
        if href.endswith('.xlsx') or href.endswith('.xls'):
            full_url = urljoin(url, href)
            xlsx_file_links.append(full_url.replace(' ', '%20'))

    return xlsx_file_links

def download_xlsx_files(url:str) -> None:
    for schedule_link in get_set_xlsx_links(url=os.getenv('WEBSITE_LINK')):
        response = requests.get(schedule_link)
        with open(f'schedules/{schedule_link.split("/")[-1]}', 'wb') as f:
            f.write(response.content)  
            
print(download_xlsx_files(url = os.getenv('WEBSITE_LINK')))