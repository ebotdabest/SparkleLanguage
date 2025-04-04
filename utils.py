def is_string(obj: str):
    if obj.startswith('"') and obj.endswith('"') or obj.startswith("'") and obj.endswith("'"): return True
    else: return False