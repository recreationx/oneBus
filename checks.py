class Validator:
    """
    A data-validation class to clean/check all values in requests
    
    TODO:
    - basic SQLi cleaning
    - strict type checking
    - data validation (value too large etc)
    """

    def __init__(self):
        pass
        
    def paramCheckExist(self, requiredParams, paramsDict):
        return requiredParams == list(paramsDict)
        
        
    def isFloat(self, value):
        """Check if a value is a number (float)

        Args:
            value (str):

        Returns:
            bool: True or False
        """
        try:
            float(value)
        except ValueError:
            print(f"isFloat: {value} is not a valid floating point value.")
            return False
        return True