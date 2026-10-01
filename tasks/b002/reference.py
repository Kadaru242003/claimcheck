import json

def count_records(path):
    with open(path) as f:
        return len(json.load(f))
