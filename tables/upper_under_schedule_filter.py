import pandas as pd
from datetime import datetime

def get_upper_under_week_type() -> int:
    # ISO-неделя: 1, 3, 5... (Нечетная) -> Тип 1 (I)
    # ISO-неделя: 2, 4, 6... (Четная) -> Тип 2 (II)
    week_num = datetime.now().isocalendar()[1]
    return 1 if week_num % 2 != 0 else 2

async def filter(df: pd.DataFrame, week_type: int = None) -> pd.DataFrame:
    if df.empty:
        return df
        
    target_type = week_type if week_type is not None else get_upper_under_week_type()
    
    def is_target_row(row_idx):
        # relative_idx: 0, 1, 2, 3... внутри дня
        relative_idx = (int(row_idx) - 2) % 14
        
        if target_type == 1: # НЕДЕЛЯ I (Нечетная года)
            # Если раньше было == 0 и не работало, меняем на != 0
            # Теперь она будет брать НИЖНЮЮ строку из пары в Pandas
            return relative_idx % 2 != 0 
        else: # НЕДЕЛЯ II (Четная года)
            # А тут наоборот — ВЕРХНЮЮ
            return relative_idx % 2 == 0

    return df[df.index.map(is_target_row)]