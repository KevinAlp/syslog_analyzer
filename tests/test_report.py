import unittest

from logforge.model import ErrorEvent, WarningEvent
from logforge.report import generate_json, generate_text


class ReportTests(unittest.TestCase):
    def test_generate_text_empty(self) -> None:
        report = generate_text([])
        self.assertIn("No errors or warnings detected.", report)

    def test_generate_text_counts(self) -> None:
        events = [
            ErrorEvent(type="fatal", message="boom"),
            WarningEvent(type="compiler_warning", message="minor issue"),
        ]
        report = generate_text(events)
        self.assertIn("Errors: 1 unique, 1 occurrences", report)
        self.assertIn("Warnings: 1 unique, 1 occurrences", report)

    def test_generate_json_fields(self) -> None:
        event = ErrorEvent(
            type="ValueError",
            message="bad",
            file="/tmp/app.py",
            line=3,
            function="run",
        )
        payload = generate_json([event])
        self.assertIn('"level": "ERROR"', payload)
        self.assertIn('"type": "ValueError"', payload)
        self.assertIn('"file": "/tmp/app.py"', payload)


if __name__ == "__main__":
    unittest.main()
