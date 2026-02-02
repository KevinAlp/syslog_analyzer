import selectors
import subprocess
import sys
from typing import List

from .analyzer import Analyzer


def run_command(command: List[str], analyzer: Analyzer) -> int:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    selector = selectors.DefaultSelector()
    assert process.stdout is not None
    assert process.stderr is not None
    selector.register(process.stdout, selectors.EVENT_READ, (process.stdout, sys.stdout))
    selector.register(process.stderr, selectors.EVENT_READ, (process.stderr, sys.stderr))

    while selector.get_map():
        for key, _ in selector.select():
            stream, output = key.data
            line = stream.readline()
            if line == "":
                selector.unregister(stream)
                continue
            output.write(line)
            output.flush()
            analyzer.process_line(line)

    return process.wait()
