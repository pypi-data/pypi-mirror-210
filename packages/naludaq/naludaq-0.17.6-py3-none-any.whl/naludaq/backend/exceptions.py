from http import HTTPStatus


class HttpError(Exception):
    def __init__(self, status_code: HTTPStatus, response: dict, *args: object):
        """Exception for HTTP errors received from the backend.

        Args:
            status_code (HTTPStatus): the error status code
            response (dict): the response JSON sent by the backend
        """
        super().__init__(*args)
        self._status_code = status_code
        self._error_id = response["error_id"]
        self._message = response["message"]

    @property
    def status_code(self) -> HTTPStatus:
        """Get the error status code"""
        return self._status_code

    @property
    def error_id(self) -> int:
        """Get the error ID"""
        return self._error_id

    @property
    def message(self) -> str:
        """Get the error message"""
        return self._message

    def raise_typed(self):
        """Raise the error as a specific type depending on the error ID"""
        type = {
            0: BackendError,
            1: ValueError,
            2: ConnectionError,
            3: DeviceError,
            4: ConnectionError,
            5: ConnectionError,
            6: ConnectionError,
            7: AcquisitionError,
            8: ValueError,
            9: ValueError,
            10: IndexError,
            11: AcquisitionError,
            12: BackendError,
            13: TimeoutError,
        }.get(self.error_id, BackendError)
        message = f"[Status {self.status_code}, ID {self.error_id}] {self.message}"
        exception = type(message)
        raise exception


class BackendError(Exception):
    pass


class BackendUnreachableError(BackendError):
    pass


class ConnectionError(BackendError):
    pass


class AcquisitionError(BackendError):
    pass


class ContextError(BackendError):
    pass


class DeviceError(BackendError):
    pass
