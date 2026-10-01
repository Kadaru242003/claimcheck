def histogram(values, bins):
    lo, hi = min(values), max(values)
    width = (hi - lo) / bins or 1
    counts = [0] * bins
    for v in values:
        i = min(int((v - lo) / width), bins - 1)
        counts[i] += 1
    return counts
