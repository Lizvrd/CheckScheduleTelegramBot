import pandas as pd
import os

testWork = pd.read_excel(os.path.join('schedules/semester/Расписание%20занятий%20П,%20оч.%20форма%20обучения,%20весенний%20семестр%202025-2026%20уч.г..xlsx'),sheet_name='11')
# TODO:
#     1. реализовать поиск по группе
#     2. вывести как строку расписание на сегодня
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    with open('text1.txt', 'w', encoding='utf-8') as f:
        f.write(testWork.to_string())
    print('Done')
    