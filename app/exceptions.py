class APIError(Exception):
    pass


class UnknownAPIError(APIError):
    pass


class ServiceUnavailableError(APIError):
    pass


class NotfoundExceptionError(APIError):
    pass