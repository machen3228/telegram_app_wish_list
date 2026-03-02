class NotFoundInDbError(LookupError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class AlreadyExistsInDbError(LookupError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
