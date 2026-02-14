import pandas as pd
import os
from typing import List

def get_exist_groups(dir: str) -> List[str]:
    exist_groups = []

    for root, dirs, files in os.walk(dir):
        for file in files:
            # xlsx = pd.read_excel(os.path.join(root, file))            
            all_sheets = pd.read_excel(os.path.join('schedules/exams/Расписание%20экзаменов%20П%20осенний%20семестр%20%202025-26%20уч%20год.xlsx'), sheet_name=None)
            for sheet_names, xlsx in all_sheets.items():
                column = xlsx['Unnamed: 0'].to_list()
                for item in column:
                    item = str(item)

                    if len(item) not in range(0,2) and item not in ['nan', 'группа', 'группы']:
                        filtered = item.split(' ')

                        if filtered[0] not in exist_groups:
                            exist_groups.append(filtered[0])
    return exist_groups

print(get_exist_groups('schedules/exams'))


# xlsx = pd.read_excel('schedules/exams/Расписание%20экзаменов%20П%20осенний%20семестр%20%202025-26%20уч%20год.xlsx')
# column = xlsx['Unnamed: 0'].to_list()
# access_groups = []
# for item in column:
#     item = str(item)
#     if len(item) not in range(0,2) and item not in ['nan', 'группа']:
#         filtered = item.split(' ')
#         access_groups.append(filtered[0])
