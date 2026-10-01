def binary_to_int(bits):
    n = 0
    for b in bits:
        n = n * 2 + (b == '1')
    return n
