import asyncio
import pandas as pd

async def read_excel_async(path: str, sheet_name: str, header: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, pd.read_excel, path)