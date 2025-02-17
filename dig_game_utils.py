
def constrain(val, min_val, max_val):
    out = val
    if val < min_val:
        out = min_val
    elif val > max_val:
        out = max_val
    return out
