import pandas as pd
import os
from typing import List
import asyncio

async def get_all_exist_groups(dir: str) -> List[str]:
    """Функция для получения списка существующих групп
    
    Args:
        dir (str): Директория с файлами

    Returns:
        List[str]: Список существующих групп
    """
    exist_groups = set()

    for root, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                all_sheets_dict = pd.read_excel(file_path, sheet_name=None)
            except Exception as e:
                print(f"Ошибка чтения файла {file}: {e}")
                continue

            for sheet_name, df in all_sheets_dict.items():
                
                if df.empty:
                    continue
                
                column_data = []
                
                if 'Unnamed: 0' in df.columns:
                    if df['Unnamed: 0'].dtype != 'str': 
                        if 'Unnamed: 1' in df.columns:
                            column_data = df['Unnamed: 1'].tolist()
                    else:
                        column_data = df['Unnamed: 0'].tolist()
                elif 'Unnamed: 1' in df.columns:
                    column_data = df['Unnamed: 1'].tolist()
                
                if not column_data:
                    continue

                for item in column_data:
                    item = str(item)

                    # Фильтрация мусора и заголовков
                    if len(item) > 2 and (item not in ['nan', 'group', 'группа', 'группы', 'Группы']):
                        filtered = item.split(' ')
                        # Безопасное получение тега группы
                        if filtered:
                            group_tag = filtered[0] if len(filtered[0]) == 8 else filtered[0][0:9]
                            exist_groups.add(group_tag)

    return list(exist_groups)