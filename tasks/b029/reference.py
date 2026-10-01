import csv
def count_rows(path):
    with open(path, newline='') as f:
        return sum(1 for _ in csv.DictReader(f))
