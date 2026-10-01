def find_index(items, target):
    for i, x in enumerate(items):
        if x == target:
            return i
    return -1
