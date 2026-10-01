def line_count(path):
    with open(path) as f:
        return sum(1 for line in f if line.strip())
