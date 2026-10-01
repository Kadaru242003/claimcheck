from collections import Counter
def is_anagram(a, b):
    return Counter(a) == Counter(b)
