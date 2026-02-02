# syslog_analyzer (logforge)

Student-level project: a small command-line tool (Python) that reads logs (or a program’s output) and produces a summary of errors/warnings.

It groups identical issues and shows occurrence counts (and file/line when available).

## Features

- Analyze a file or stdin.
- Run a command and analyze its output in real time.
- Detect common patterns (compiler diagnostics, Python tracebacks, GDB signals, keyword lines like `ERROR`/`WARNING`).
- Text report or JSON (`--json`).

## Requirements

- Python 3.8+.

## Quick start

From the project root:

```bash
cd /path/to/syslog_analyzer  # <-- change this
```

There are two entry points:

- `./bin/logforge`: the “official” CLI (subcommands `analyze` / `run`)
- `./bin/syslog`: a small bash wrapper for quicker usage

## Usage (`logforge`)

```bash
./bin/logforge --help
```

```bash
./bin/logforge analyze path/to/my_log.txt  # <-- change this
```

```bash
cat path/to/my_log.txt | ./bin/logforge analyze  # <-- change this
```

```bash
./bin/logforge analyze path/to/my_log.txt --json  # <-- change this
```

```bash
./bin/logforge run -- make test
```

## Usage (`syslog`)

`bin/syslog` tries to “do the right thing”:

- `syslog my_log.txt` → analyze the file
- `syslog my_script.py` → run `python3 my_script.py` and analyze its output
- `syslog my_file.c` / `syslog my_header.h` → compile-check (`-fsyntax-only`) and analyze output
- `syslog <command …>` → run the command and analyze output

```bash
./bin/syslog my_script.py
./bin/syslog my_file.c --json
```

After installing into your `PATH`:

```bash
syslog my_script.py
syslog my_script.py -- --arg1 123
syslog my_file.c --json
syslog run -- make test
```

To pass arguments to a Python script, use `--` (example: `syslog script.py -- --flag 1`).

### Install `syslog` into your PATH

This creates a `syslog` symlink in a common bin directory (usually `~/.local/bin`):

```bash
chmod +x bin/syslog bin/install-syslog
./bin/install-syslog
```

To install into another directory, pass a prefix (then add it to your `PATH`):

```bash
./bin/install-syslog "$HOME/bin"  # <-- change this
```

To install system-wide (for all users), use `/usr/local/bin` (may require `sudo`):

```bash
sudo ./bin/install-syslog /usr/local/bin
```

```bash
export PATH="$HOME/.local/bin:$PATH"
```

If you already have a `syslog` command on your machine, install under another name (example: `syslog-analyze`):

```bash
./bin/install-syslog "$HOME/.local/bin" syslog-analyze
export PATH="$HOME/.local/bin:$PATH"  # <-- change this if needed
syslog-analyze my_script.py
```

## Notes / limitations

- This is pattern-based: it recognizes common formats, but it will not catch every possible error line.
- `syslog my_file.c` / `syslog my_header.h` requires a C compiler (`cc`). On macOS, this is typically `clang` via Xcode Command Line Tools.
- `journalctl` is Linux-specific. On macOS, analyze a log file, or pipe output from another command.

## Development

```bash
python3 -m unittest
```

```bash
python3 tests/test_ulti.py 2>&1 | ./bin/logforge analyze
```

## Troubleshooting

- `syslog: command not found`: make sure `~/.local/bin` is in your `PATH` (or run `./bin/syslog ...`).
- On macOS (zsh), to make the `PATH` change persistent, add the export line to `~/.zshrc` and restart your terminal.
- `cc: command not found`: the C-check feature needs a C compiler (install one, or use `logforge analyze` on an existing log file).
- If `syslog` prints `No errors or warnings detected.` when you expected errors, retry after reinstalling the link: `./bin/install-syslog`.
- If you see Python `Permission denied` errors related to `__pycache__`/`.pyc` when running tests, use: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest`.

## Uninstall

```bash
rm -f ~/.local/bin/syslog ~/.local/bin/syslog-analyze  # <-- change this
```

## License

MIT — see `LICENSE`.
