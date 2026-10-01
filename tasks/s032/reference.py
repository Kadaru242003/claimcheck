from collections import Counter
def most_common_char(s):
    c = Counter(s)
    return min(c, key=lambda ch: (-c[ch], ch))
