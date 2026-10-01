def from_hms(text):
    h, m, s = (int(p) for p in text.split(':'))
    return h * 3600 + m * 60 + s
