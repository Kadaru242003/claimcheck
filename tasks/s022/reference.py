def snake_to_camel(name):
    parts = [p for p in name.split('_') if p]
    if not parts:
        return ""
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])
