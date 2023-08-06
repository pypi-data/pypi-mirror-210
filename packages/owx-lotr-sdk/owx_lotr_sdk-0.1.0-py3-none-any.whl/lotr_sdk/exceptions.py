"""This module contains the custom exceptions used in the SDK."""


class InvalidAPIKeyError(ValueError):
    """Raised when the API key provided is empty or invalid."""

    def __init__(self, message="The provided API key is empty or invalid."):
        self.message = message
        super().__init__(self.message)


class InvalidClauseError(ValueError):
    """Raised when the clause used in the query is not supported or is
    invalid."""

    def __init__(self,
                 message="The provided clause in the query is not "
                 "supported or is invalid."):
        self.message = message
        super().__init__(self.message)


class DuplicateClauseError(ValueError):
    """Raised when the clause used in the query does not support multiple
    values, but multiple values are provided."""

    def __init__(self,
                 message="The provided clause in the query does not support "
                 "multiple values, but multiple values are provided."):
        self.message = message
        super().__init__(self.message)


class InvalidModelDictionaryError(ValueError):
    """Raised when the dictionary used to create the model is invalid."""

    def __init__(self,
                 dictionary,
                 message="The provided dictionary used to create the "
                 "model is empty or invalid."):
        self.message = message
        if dictionary is not None:
            self.message += f" Type: {type(dictionary)} Value: {dictionary}"
        super().__init__(self.message)
