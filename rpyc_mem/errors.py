"""Rpyc Memory Errors"""


class BaseRpycMemError(Exception):
    """Base RPyC memory error"""
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


class RpycMemSvcError(BaseRpycMemError):
    """Error associated to RPyC memory service"""
    def __init__(self, message=None):
        super().__init__(
            message or 'An unspecified error occurred in RpycMemService'
        )


class RpycMemConnError(BaseRpycMemError):
    """Error associated to Rpyc memory connection"""
    def __init__(self, message=None):
        super().__init__(
            message or 'An unspecified error occurred in RpycMemConnect'
        )


class RpycMemError(BaseRpycMemError):
    """Error associated to Rpyc memory object"""
    def __init__(self, message=None):
        super().__init__(
            message or 'An unspecified error occurred in RpycMem'
        )
