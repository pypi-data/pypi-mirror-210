from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetTasksRequest(_message.Message):
    __slots__ = ["company_id", "is_completed", "is_paid", "is_signed", "user_id"]
    COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
    IS_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    IS_PAID_FIELD_NUMBER: _ClassVar[int]
    IS_SIGNED_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    company_id: int
    is_completed: bool
    is_paid: bool
    is_signed: bool
    user_id: int
    def __init__(self, company_id: _Optional[int] = ..., user_id: _Optional[int] = ..., is_completed: bool = ..., is_paid: bool = ..., is_signed: bool = ...) -> None: ...

class GetTasksResponse(_message.Message):
    __slots__ = ["tasks"]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(self, tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ["company_user_id", "description", "from_date", "id", "is_completed", "is_paid", "is_signed", "payment_datetime", "price", "state", "title", "to_date"]
    COMPANY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    IS_PAID_FIELD_NUMBER: _ClassVar[int]
    IS_SIGNED_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_DATETIME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    company_user_id: int
    description: str
    from_date: str
    id: int
    is_completed: bool
    is_paid: bool
    is_signed: bool
    payment_datetime: str
    price: str
    state: str
    title: str
    to_date: str
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., price: _Optional[str] = ..., from_date: _Optional[str] = ..., to_date: _Optional[str] = ..., is_completed: bool = ..., is_paid: bool = ..., is_signed: bool = ..., state: _Optional[str] = ..., payment_datetime: _Optional[str] = ..., company_user_id: _Optional[int] = ...) -> None: ...
