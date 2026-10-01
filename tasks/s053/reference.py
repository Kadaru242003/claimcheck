def reverse_int(n):
    r = int(str(abs(n))[::-1])
    return -r if n < 0 else r
