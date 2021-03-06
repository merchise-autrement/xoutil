from datetime import *
from typing import *

def new_date(d: date) -> date: ...
def new_datetime(d: date) -> datetime: ...
def strfdelta(delta: timedelta) -> str: ...
def strftime(dt: date, fmt: str) -> str: ...
def parse_date(value: str = None) -> date: ...
def parse_datetime(value: str = None) -> datetime: ...
def get_month_first(ref: date = None) -> date: ...
def get_month_last(ref: date = None) -> date: ...
def get_next_month(ref: date = None, lastday: bool = False) -> date: ...
def is_full_month(start: date, end: date) -> bool: ...

class flextime(timedelta):
    @classmethod
    def parse_simple_timeformat(cls, which: str) -> Tuple[int, int, int]: ...

class TimeSpan:
    start_date: Optional[date]
    end_date: Optional[date]
    def __init__(
        self, start_date: Union[str, date] = None, end_date: Union[str, date] = None
    ) -> None: ...
    @classmethod
    def from_date(self, date: date) -> "TimeSpan": ...
    @property
    def past_unbound(self) -> bool: ...
    @property
    def future_unbound(self) -> bool: ...
    @property
    def unbound(self) -> bool: ...
    @property
    def bound(self) -> bool: ...
    @property
    def valid(self) -> bool: ...
    def __contains__(self, other: date) -> bool: ...
    def overlaps(self, other: "TimeSpan") -> bool: ...
    def isdisjoint(self, other: "TimeSpan") -> bool: ...
    def __le__(self, other: "TimeSpan") -> bool: ...
    def issubset(self, other: "TimeSpan") -> bool: ...
    def __lt__(self, other: "TimeSpan") -> bool: ...
    def __gt__(self, other: "TimeSpan") -> bool: ...
    def __ge__(self, other: "TimeSpan") -> bool: ...
    def covers(self, other: "TimeSpan") -> bool: ...
    def issuperset(self, other: "TimeSpan") -> bool: ...
    def __iter__(self) -> Iterator[date]: ...
    def __getitem__(self, index: int) -> date: ...
    def __eq__(self, other) -> bool: ...
    def __and__(self, other: "TimeSpan") -> "TimeSpan": ...
    def __lshift__(self, delta: Union[int, timedelta]) -> "TimeSpan": ...
    def __rshift__(self, delta: Union[int, timedelta]) -> "TimeSpan": ...
    def intersection(self, *others: "TimeSpan") -> "TimeSpan": ...
    def diff(self, other: "TimeSpan") -> Tuple[TimeSpan, TimeSpan]: ...

class DateTimeSpan(TimeSpan):
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    def __init__(
        self,
        start_datetime: Union[str, date] = None,
        end_datetime: Union[str, date] = None,
    ) -> None: ...
    @classmethod
    def from_date(self, d: date) -> "DateTimeSpan": ...
    @classmethod
    def from_datetime(self, dt: datetime) -> "DateTimeSpan": ...
    @classmethod
    def from_timespan(self, ts: TimeSpan) -> "DateTimeSpan": ...
    def __iter__(self) -> Iterator[datetime]: ...
    def __getitem__(self, index: int) -> datetime: ...
    def __and__(self, other: TimeSpan) -> "DateTimeSpan": ...
    def __lshift__(self, delta: Union[int, timedelta]) -> "DateTimeSpan": ...
    def __rshift__(self, delta: Union[int, timedelta]) -> "DateTimeSpan": ...
    def intersection(self, *others: TimeSpan) -> "DateTimeSpan": ...
    def diff(self, other: TimeSpan) -> Tuple["DateTimeSpan", "DateTimeSpan"]: ...

EmptyTimeSpan: DateTimeSpan
