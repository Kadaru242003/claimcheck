def is_isogram(word):
    letters = [c.lower() for c in word if c.isalpha()]
    return len(letters) == len(set(letters))
