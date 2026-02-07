import re

def validate_group_format(text: str) -> bool:
    pattern = r'^[Бб]\d{2}-\d{3}-\d$'
    return bool(re.match(pattern, text))