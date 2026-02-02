import unittest

from logforge.analyzer import Analyzer


class AnalyzerTests(unittest.TestCase):
    def test_compiler_warning(self) -> None:
        analyzer = Analyzer()
        analyzer.process_line("main.c:10:5: warning: unused variable 'x'\n")
        events = analyzer.get_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.level, "WARNING")
        self.assertEqual(event.type, "compiler_warning")
        self.assertEqual(event.file, "main.c")
        self.assertEqual(event.line, 10)

    def test_python_traceback(self) -> None:
        analyzer = Analyzer()
        lines = [
            "Traceback (most recent call last):\n",
            '  File "/tmp/app.py", line 42, in run\n',
            "    raise ValueError('bad')\n",
            "ValueError: bad\n",
        ]
        for line in lines:
            analyzer.process_line(line)
        events = analyzer.get_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.level, "ERROR")
        self.assertEqual(event.type, "ValueError")
        self.assertEqual(event.file, "/tmp/app.py")
        self.assertEqual(event.line, 42)
        self.assertEqual(event.function, "run")

    def test_gdb_signal_with_location(self) -> None:
        analyzer = Analyzer()
        analyzer.process_line("Program received signal SIGSEGV, Segmentation fault.\n")
        analyzer.process_line("#0  main () at main.c:12\n")
        events = analyzer.get_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.level, "ERROR")
        self.assertEqual(event.type, "SIGSEGV")
        self.assertEqual(event.file, "main.c")
        self.assertEqual(event.line, 12)
        self.assertEqual(event.function, "main")

    def test_generic_error(self) -> None:
        analyzer = Analyzer()
        analyzer.process_line("ERROR: failed to open config at config.yml:9\n")
        events = analyzer.get_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.level, "ERROR")
        self.assertEqual(event.type, "unknown_error")
        self.assertEqual(event.file, "config.yml")
        self.assertEqual(event.line, 9)

    def test_pending_signal_flushes_on_finalize(self) -> None:
        analyzer = Analyzer()
        analyzer.process_line("SIGABRT\n")
        self.assertEqual(len(analyzer.get_events()), 0)
        analyzer.finalize()
        events = analyzer.get_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.type, "SIGABRT")


if __name__ == "__main__":
    unittest.main()
