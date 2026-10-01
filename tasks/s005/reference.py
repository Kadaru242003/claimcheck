from collections import Counter

def top_k_words(text, k):
    counts = Counter(w.lower() for w in text.split())
    return [w for w, _ in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:k]]
