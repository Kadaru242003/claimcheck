from collections import Counter
def top_word(text):
    c = Counter(text.lower().split())
    return min(c, key=lambda w: (-c[w], w))
