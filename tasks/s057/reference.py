def longest_word(text):
    best = ''
    for w in text.split():
        if len(w) > len(best):
            best = w
    return best
