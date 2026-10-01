def count_leap_years(start, end):
    return sum(1 for y in range(start, end + 1) if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))
