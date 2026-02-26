import pandas as pd
from datetime import datetime

def get_upper_under_week_type() -> int:
    # 26.02.2026 — это 9-я неделя года (нечетная)
    today = datetime.now()
    return datetime.isocalendar(today)[1]

async def filter(df: pd.DataFrame):
    if df.empty:
        return df
        
    week_num = get_upper_under_week_type()
    # Настраиваем: остаток 1 (нечетная) -> I неделя, остаток 0 (четная) -> II неделя
    # Если недели в боте перепутаны, просто поменяй 'I' на 'II'
    target_week_type = 'I' if week_num % 2 != 0 else 'II'
    
    # В твоих файлах: 
    # Понедельник начинается со строки 2, Вторник с 16 и т.д. (шаг 14)
    # Нам нужно понять: текущая строка — это верхняя часть пары или нижняя?
    
    def is_target_row(row_idx):
        # Позиция строки внутри блока дня (0-13)
        # Так как WEEK_DAYS[0] = 2, мы вычитаем смещение, чтобы начать отсчет с 0
        relative_idx = (row_idx - 2) % 14
        
        # relative_idx: 0, 2, 4, 6, 8, 10, 12 — это всегда 'I' неделя (верхняя строка)
        # relative_idx: 1, 3, 5, 7, 9, 11, 13 — это всегда 'II' неделя (нижняя строка)
        
        if target_week_type == 'II':
            return relative_idx % 2 == 0
        else:
            return relative_idx % 2 != 0

    # Применяем фильтр на основе относительного индекса
    filtered = df[df.index.map(is_target_row)]
    
    return filtered