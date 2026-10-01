from datetime import date
def day_of_year(year, month, day):
    return date(year, month, day).timetuple().tm_yday
