class TileserverException(Exception):
    """Base Tileserver Exsception."""
    pass

class MissingArgument(TileserverException):
    def __init__(self, argument):
        super().__init__("Missing argument: " + str(argument))

class EndpointError(TileserverException):
    def __init__(self, error_message):
        super().__init__("Tileserver threw an error: " + str(error_message))

class WrongDirection(TileserverException):
    def __init__(self, wrong, right):
        if len(right) > 1:
            right = " or ".join(r for r in right)
        else:
            right = right[0]
        super().__init__("Direction " + str(wrong) + " cannot be used. Must be " + right)

class UnknownStyle(TileserverException):
    def __init__(self, style):
        super().__init__(style)