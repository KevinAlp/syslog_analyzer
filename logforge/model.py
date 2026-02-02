from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EventKey:
    level: str
    type: str
    message: str
    file: Optional[str]
    line: Optional[int]
    function: Optional[str]


@dataclass
class Event:
    level: str
    type: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    function: Optional[str] = None
    occurrences: int = 1

    def key(self) -> EventKey:
        return EventKey(
            level=self.level,
            type=self.type,
            message=self.message,
            file=self.file,
            line=self.line,
            function=self.function,
        )


class ErrorEvent(Event):
    def __init__(
        self,
        type: str,
        message: str,
        file: Optional[str] = None,
        line: Optional[int] = None,
        function: Optional[str] = None,
    ) -> None:
        super().__init__(
            level="ERROR",
            type=type,
            message=message,
            file=file,
            line=line,
            function=function,
        )


class WarningEvent(Event):
    def __init__(
        self,
        type: str,
        message: str,
        file: Optional[str] = None,
        line: Optional[int] = None,
        function: Optional[str] = None,
    ) -> None:
        super().__init__(
            level="WARNING",
            type=type,
            message=message,
            file=file,
            line=line,
            function=function,
        )
