import pandas as pd
import os
from typing import List
import asyncio

async def get_exist_groups(dir: str) -> List[str]:
    exist_groups = []

    for root, dirs, files in os.walk(dir):
        for file in files:
            all_sheets = pd.read_excel(os.path.join(root, file))    
                    
            for sheet_names, xlsx in all_sheets.items():
                if all_sheets['Unnamed: 0'].dtype != 'str':
                    column = all_sheets['Unnamed: 1'].tolist()
                else:
                    column = all_sheets['Unnamed: 0'].tolist()
                for item in column:
                    item = str(item)

                    if len(item) not in range(0,2) and (item not in ['nan', 'группа', 'группы', 'Группы']):
                        filtered = item.split(' ')
                        group_tag = filtered[0] if len(filtered[0]) == 8 else filtered[0][0:9]
                        if group_tag not in exist_groups:
                            exist_groups.append(group_tag)
                        else: continue
    return exist_groups


async def main():
    exist_groups = await get_exist_groups('schedules/exams')
    print(exist_groups)

if __name__ == '__main__':
    asyncio.run(main())