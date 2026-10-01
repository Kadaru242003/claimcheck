def caesar(text, shift):
    out = []
    for c in text:
        if c.isalpha() and c.isascii():
            base = ord('A') if c.isupper() else ord('a')
            out.append(chr((ord(c) - base + shift) % 26 + base))
        else:
            out.append(c)
    return "".join(out)
