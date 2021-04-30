class Validator:
    """
    A data-validation class to clean/check all values in requests
    """

    def __init__(self):
        pass

    def isFloat(self, *args):
        """Check if a value is a number (float)

        Args:
            value (str):

        Returns:
            bool: True or False
        """
        for value in args:
            try:
                float(value)
            except ValueError:
                print(f"isFloat: {value} is not a valid floating point value.")
                return False
        return True

    def inputCheck(self, paramsDict):
        for value in paramsDict.values():
            if len(value.replace(" ", "")) == 0:
                return False
            if not self.isFloat(value):
                return False
        return True

    def selectCheck(self, *options):
        """Check if any selected option is of default
        value

        Returns:
            bool: True if default value does not exist
            and False if default value exists
        """
        return not any("default" in option for option in options)
