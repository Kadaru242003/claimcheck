def is_armstrong(n):
    d = str(n)
    return n == sum(int(c) ** len(d) for c in d)
