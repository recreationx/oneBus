def isFloat(value):
    try:
        float(value)
    except ValueError:
        return False
    return True
