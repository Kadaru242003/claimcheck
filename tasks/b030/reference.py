def longest_line(path):
    with open(path) as f:
        return max((line.rstrip('\n') for line in f), key=len, default='')
