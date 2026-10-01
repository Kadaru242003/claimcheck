def safe_int(text, default):
    try:
        return int(text)
    except ValueError:
        return default
