from get_all_exist_group import get_exist_groups
from asyncio import run, create_task
import pandas as pd
import os
import re

async def check_exist_groups(user_text: str) -> bool:
    exist_groups = await get_exist_groups(dir='schedules/exams')
    if user_text in exist_groups:
        return True
    else:
        return False
async def main():
    print(await check_exist_groups('Б24-281-1'))

run(main())