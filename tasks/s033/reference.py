import csv
def parse_csv_line(line):
    return next(csv.reader([line]))
