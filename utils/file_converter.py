import os
async def rename_xls_to_xlsx(dir: str) -> None:
        for root, dirs, files in os.walk('schedules/'):
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file.endswith('.xls'):
                        old_path = os.path.join(root, file)
                        new_path = os.path.join(root, file[:-4] + '.xlsx')
                        os.rename(old_path, new_path)