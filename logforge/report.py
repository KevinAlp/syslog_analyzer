import json
from typing import Iterable, List

from .model import Event


def _format_location(event: Event) -> str:
    parts: List[str] = []
    if event.file:
        if event.line is not None:
            parts.append(f"{event.file} (Line {event.line})")
        else:
            parts.append(event.file)
    if event.function:
        parts.append(f"in {event.function}")
    return " ".join(parts)


def generate_text(events: Iterable[Event]) -> str:
    event_list = list(events)
    if not event_list:
        return "No errors or warnings detected."

    errors = [e for e in event_list if e.level == "ERROR"]
    warnings = [e for e in event_list if e.level == "WARNING"]

    def total_occurrences(items: List[Event]) -> int:
        return sum(e.occurrences for e in items)

    lines: List[str] = []
    if errors:
        lines.append(
            f"Errors: {len(errors)} unique, {total_occurrences(errors)} occurrences"
        )
        for event in sorted(errors, key=lambda e: (-e.occurrences, e.type, e.message)):
            location = _format_location(event)
            count = f" ({event.occurrences}x)" if event.occurrences > 1 else ""
            lines.append(
                f"- [{event.level}] {event.type}{count}: {event.message}"
            )
            if location:
                lines.append(f"  Location: {location}")
    if warnings:
        lines.append(
            f"Warnings: {len(warnings)} unique, {total_occurrences(warnings)} occurrences"
        )
        for event in sorted(
            warnings, key=lambda e: (-e.occurrences, e.type, e.message)
        ):
            location = _format_location(event)
            count = f" ({event.occurrences}x)" if event.occurrences > 1 else ""
            lines.append(
                f"- [{event.level}] {event.type}{count}: {event.message}"
            )
            if location:
                lines.append(f"  Location: {location}")

    return "\n".join(lines)


def generate_json(events: Iterable[Event]) -> str:
    payload = []
    for event in events:
        payload.append(
            {
                "level": event.level,
                "type": event.type,
                "message": event.message,
                "file": event.file,
                "line": event.line,
                "function": event.function,
                "occurrences": event.occurrences,
            }
        )
    return json.dumps(payload, indent=2, sort_keys=True)
