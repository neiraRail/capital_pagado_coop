# src/utils/dates.py

def get_previous_period(year: int, month: int):
    if month == 1:
        return year - 1, 12
    return year, month - 1
