def count_starting(text, letter):
    return sum(w.lower().startswith(letter.lower()) for w in text.split())
