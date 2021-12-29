from datetime import datetime


def get_numbers_as_string(date: datetime):
    day = date.day if date.day > 9 else "0{}".format(date.day)
    month = date.month if date.month > 9 else "0{}".format(date.month)
    return day, month, date.year
