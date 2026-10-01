import calendar
def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]
