class AmberUserError(Exception):
    """Raised to indicate an error in SDK usage"""

    def __init__(self, message):
        self.message = message


class AmberCloudError(Exception):
    """Raised upon any non-200 response from the Amber cloud"""

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__("{}: {}".format(code, message))
