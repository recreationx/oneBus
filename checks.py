def isFloat(value):
    """Check if a value is a number (float)

    Args:
        value (str):

    Returns:
        bool: True or False
    """
    try:
        float(value)
    except ValueError:
        return False
    return True
