import csv
def sum_column(path, column):
    with open(path, newline='') as f:
        return sum(float(r[column]) for r in csv.DictReader(f))
