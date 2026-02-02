import re
from collections import deque
from typing import Deque, Dict, Iterable, List, Optional, Tuple

from .model import ErrorEvent, Event, EventKey, WarningEvent


class Analyzer:
    def __init__(self, context_lines: int = 20) -> None:
        self._buffer: Deque[str] = deque(maxlen=context_lines)
        self._events: Dict[EventKey, Event] = {}
        self._traceback_active = False
        self._traceback_last_location: Optional[Tuple[str, int, Optional[str]]] = None
        self._pending_signal: Optional[Tuple[str, str]] = None

        self._compiler_re = re.compile(
            r"^(?P<file>[^:\s]+):(?P<line>\d+):"
            r"(?:(?P<col>\d+):)?\s*(?P<level>warning|error):\s*(?P<msg>.*)$",
            re.IGNORECASE,
        )
        self._traceback_start_re = re.compile(r"^Traceback \(most recent call last\):")
        self._traceback_file_re = re.compile(
            r'^\s*File "([^"]+)", line (\d+)(?:, in ([\w<>]+))?'
        )
        self._traceback_exc_re = re.compile(
            r"^\s*([A-Za-z_][\w\.]*)(?::\s*(.*))?$"
        )
        self._gdb_signal_re = re.compile(r"Program received signal\s+(SIG[A-Z0-9]+)")
        self._gdb_signal_short_re = re.compile(r"^(SIG[A-Z0-9]+)\b")
        self._gdb_location_re = re.compile(r"\bat\s+([^:\s]+):(\d+)")
        self._gdb_frame_re = re.compile(r"^#\d+\s+([^\s(]+)")
        self._generic_level_re = re.compile(
            r"\b(ERROR|WARNING|FATAL|FAILED)\b", re.IGNORECASE
        )
        self._file_line_re = re.compile(r"([A-Za-z0-9_./-]+):(\d+)")
        self._function_re = re.compile(r"\bin\s+([A-Za-z_]\w*)\b")

    def process_lines(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.process_line(line)

    def process_line(self, line: str) -> None:
        raw_line = line.rstrip("\n")
        self._buffer.append(raw_line)

        if self._traceback_start_re.match(raw_line):
            self._traceback_active = True
            self._traceback_last_location = None
            return

        if self._traceback_active:
            file_match = self._traceback_file_re.match(raw_line)
            if file_match:
                file = file_match.group(1)
                line_no = int(file_match.group(2))
                function = file_match.group(3)
                self._traceback_last_location = (file, line_no, function)
                return

            exc_match = self._traceback_exc_re.match(raw_line.strip())
            if exc_match:
                exc_type = exc_match.group(1)
                message = raw_line.strip()
                file = None
                line_no = None
                function = None
                if self._traceback_last_location:
                    file, line_no, function = self._traceback_last_location
                self._add_event(
                    ErrorEvent(
                        type=exc_type,
                        message=message,
                        file=file,
                        line=line_no,
                        function=function,
                    )
                )
                self._traceback_active = False
                self._traceback_last_location = None
                return

        compiler_match = self._compiler_re.match(raw_line)
        if compiler_match:
            file = compiler_match.group("file")
            line_no = int(compiler_match.group("line"))
            level = compiler_match.group("level").lower()
            msg = compiler_match.group("msg")
            if level == "warning":
                self._add_event(
                    WarningEvent(
                        type="compiler_warning",
                        message=msg,
                        file=file,
                        line=line_no,
                    )
                )
            else:
                self._add_event(
                    ErrorEvent(
                        type="compiler_error",
                        message=msg,
                        file=file,
                        line=line_no,
                    )
                )
            return

        if self._pending_signal:
            location_match = self._gdb_location_re.search(raw_line)
            if location_match:
                file = location_match.group(1)
                line_no = int(location_match.group(2))
                function_match = self._gdb_frame_re.match(raw_line.strip())
                function = function_match.group(1) if function_match else None
                signal, message = self._pending_signal
                self._add_event(
                    ErrorEvent(
                        type=signal,
                        message=message,
                        file=file,
                        line=line_no,
                        function=function,
                    )
                )
                self._pending_signal = None
            else:
                signal, message = self._pending_signal
                self._add_event(ErrorEvent(type=signal, message=message))
                self._pending_signal = None

        gdb_match = self._gdb_signal_re.search(raw_line)
        if not gdb_match:
            gdb_match = self._gdb_signal_short_re.match(raw_line.strip())
        if gdb_match:
            signal = gdb_match.group(1)
            self._pending_signal = (signal, raw_line.strip())
            return

        generic_match = self._generic_level_re.search(raw_line)
        if generic_match:
            keyword = generic_match.group(1).upper()
            level = "ERROR"
            event_type = "unknown_error"
            if keyword == "WARNING":
                level = "WARNING"
                event_type = "unknown_warning"
            elif keyword == "FATAL":
                event_type = "fatal"
            elif keyword == "FAILED":
                event_type = "failed"

            file, line_no = self._extract_location(raw_line)
            function = self._extract_function(raw_line)
            message = raw_line.strip()
            if level == "WARNING":
                self._add_event(
                    WarningEvent(
                        type=event_type,
                        message=message,
                        file=file,
                        line=line_no,
                        function=function,
                    )
                )
            else:
                self._add_event(
                    ErrorEvent(
                        type=event_type,
                        message=message,
                        file=file,
                        line=line_no,
                        function=function,
                    )
                )

    def _extract_location(self, line: str) -> Tuple[Optional[str], Optional[int]]:
        match = self._file_line_re.search(line)
        if not match:
            return None, None
        return match.group(1), int(match.group(2))

    def _extract_function(self, line: str) -> Optional[str]:
        match = self._function_re.search(line)
        if match:
            return match.group(1)
        return None

    def _add_event(self, event: Event) -> None:
        key = event.key()
        if key in self._events:
            self._events[key].occurrences += 1
        else:
            self._events[key] = event

    def get_events(self) -> List[Event]:
        return list(self._events.values())

    def get_recent_context(self) -> List[str]:
        return list(self._buffer)

    def finalize(self) -> None:
        if self._pending_signal:
            signal, message = self._pending_signal
            self._add_event(ErrorEvent(type=signal, message=message))
            self._pending_signal = None
