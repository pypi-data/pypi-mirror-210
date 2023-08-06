class InputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        error -- explanation of the error
    """

    def __init__(self, message):
        self.message = message