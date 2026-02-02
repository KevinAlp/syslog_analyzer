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

This creates a `syslog` symlink in `~/.local/bin`:

```bash
chmod +x bin/syslog bin/install-syslog
./bin/install-syslog
```

```bash
export PATH="$HOME/.local/bin:$PATH"
```

If you already have a `syslog` command on your machine, use another name (example: `syslog-analyze`):

```bash
mkdir -p ~/.local/bin
ln -sf "$PWD/bin/syslog" ~/.local/bin/syslog-analyze
export PATH="$HOME/.local/bin:$PATH"
syslog-analyze my_script.py
```

## Development

```bash
python3 -m unittest
```

```bash
python3 tests/test_ulti.py 2>&1 | ./bin/logforge analyze
```

## License

MIT — see `LICENSE`.
