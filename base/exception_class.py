"""
@Describe: 自定义异常类
ValueEmptyError
ValuesEmptyError
ValueNotEmptyError
ResultIsNotZeroError
LengthLTZeroError
NotContainValueError
ContainInvalidValueError
ActualNEExpectedError
"""


class DomeException(Exception):
    pass


class ServerRSPError(DomeException):
    pass


class ActualNEExpectedError(DomeException):
    pass


class ValueEmptyError(DomeException):
    pass


class ValueIsNoneError(DomeException):
    pass


class NotContainValueError(DomeException):
    pass


class ContainInvalidValueError(DomeException):
    pass


class ValuesEmptyError(DomeException):
    pass

class ActualEQExpectedError(DomeException):
    pass
