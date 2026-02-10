import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List, Any
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
    list = list_facultetes.split('\n')
    already_list = []
    
    for item in list:
        if ((len(item) in range(1, 5)) or ('филиал' in item)) and (item != '\xa0'):
            already_list.append(item)
    
    return already_list

def get_set_xlsx_links(url: str)->List[str]:
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

def filtered_schedules(url: str) -> List[str]:
    all_xlsx_list = get_set_xlsx_links(url=os.getenv('WEBSITE_LINK'))
    filtered_files = []
    
    for item in all_xlsx_list:
        xls_file = item.split('/')[-1]
        xls_file = xls_file.split('%20')
    
        if ('очная' in xls_file or 'заочная' in xls_file or 'очно-заочная' in xls_file) or ('Приложение' in xls_file) or ('над_под' in xls_file):
            continue
        else:
            filtered_files.append(item)

    return filtered_files

def download_xlsx_files(url:str) -> Any:
    for schedule_link in filtered_schedules(url=os.getenv('WEBSITE_LINK')):
        response = requests.get(schedule_link)
        
        if 'экзаменов' in schedule_link.split('%20'):
            with open(f'schedules/exams/{schedule_link.split("/")[-1]}', 'wb') as f:
                f.write(response.content)
        
        else:
            with open(f'schedules/semester/{schedule_link.split("/")[-1]}', 'wb') as f:
                f.write(response.content)