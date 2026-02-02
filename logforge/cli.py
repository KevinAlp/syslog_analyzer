import argparse
import sys
from typing import List, Optional

from .analyzer import Analyzer
from .report import generate_json, generate_text
from .runner import run_command


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logforge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a command and analyze output")
    run_parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to execute")
    run_parser.add_argument(
        "--json", action="store_true", help="Output summary as JSON"
    )

    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing output")
    analyze_parser.add_argument("source", nargs="?", help="File to read (default: stdin)")
    analyze_parser.add_argument(
        "--json", action="store_true", help="Output summary as JSON"
    )

    return parser


def _emit_report(analyzer: Analyzer, to_json: bool) -> str:
    events = analyzer.get_events()
    if to_json:
        return generate_json(events)
    return generate_text(events)


def _read_stream(source: Optional[str]) -> List[str]:
    if source:
        with open(source, "r", encoding="utf-8", errors="replace") as handle:
            return handle.readlines()
    return sys.stdin.read().splitlines(True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    if raw_argv and raw_argv[0] not in {"run", "analyze"}:
        raw_argv = ["analyze", raw_argv[0], *raw_argv[1:]]
    args = parser.parse_args(raw_argv)

    if args.command == "run":
        cmd = args.cmd
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        if not cmd:
            parser.error("run requires a command to execute")
        analyzer = Analyzer()
        exit_code = run_command(cmd, analyzer)
        analyzer.finalize()
        report = _emit_report(analyzer, args.json)
        print(report, file=sys.stderr)
        return exit_code

    if args.command == "analyze":
        analyzer = Analyzer()
        lines = _read_stream(args.source)
        analyzer.process_lines(lines)
        analyzer.finalize()
        report = _emit_report(analyzer, args.json)
        print(report)
        return 0

    parser.error("Unknown command")
    return 2
