class MyException(Exception):
    ...


class EntityNotFound(MyException):
    ...


class EntityExists(MyException):
    ...


class NullMember(MyException):
    ...


class OutOfStock(MyException):
    ...


class ToManyBorrowedBook(MyException):
    ...


class LowBalance(MyException):
    ...
