#!/usr/bin/env python3
import sys
import time
import random
import threading
import traceback

def spam_stdout():
    for i in range(20):
        print(f"[INFO] processing step {i}")
        time.sleep(0.05)

def spam_stderr():
    for i in range(10):
        print(f"[DEBUG] internal state={random.randint(0,999)}", file=sys.stderr)
        time.sleep(0.07)

def fake_compiler_output():
    messages = [
        "main.c:42:13: warning: unused variable ‘x’ [-Wunused-variable]",
        "utils.c:87:5: error: expected ';' before 'return'",
        "math.c:128:2: warning: implicit declaration of function ‘sqrt’",
    ]
    for msg in messages:
        print(msg, file=sys.stderr)
        time.sleep(0.1)

def fake_gdb_output():
    print("Program received signal SIGSEGV, Segmentation fault.", file=sys.stderr)
    time.sleep(0.1)
    print("0x000055555555515d in compute_value () at calc.c:128", file=sys.stderr)
    time.sleep(0.1)
    print("128        return array[index];", file=sys.stderr)

def python_traceback():
    try:
        def inner():
            return int("not_a_number")
        def outer():
            return inner()
        outer()
    except Exception:
        traceback.print_exc()

def generic_errors():
    messages = [
        "ERROR: connection timeout while contacting database",
        "WARNING: configuration file not found, using defaults",
        "FATAL: unable to initialize subsystem",
        "ERROR failed to allocate memory block",
    ]
    for msg in messages:
        print(msg, file=sys.stderr)
        time.sleep(0.08)

def noise():
    for i in range(30):
        print(f"random noise line {i} lorem ipsum dolor sit amet")
        time.sleep(0.02)

def main():
    threads = [
        threading.Thread(target=spam_stdout),
        threading.Thread(target=spam_stderr),
        threading.Thread(target=noise),
    ]

    for t in threads:
        t.start()

    time.sleep(0.5)
    fake_compiler_output()
    time.sleep(0.3)
    python_traceback()
    time.sleep(0.3)
    fake_gdb_output()
    time.sleep(0.3)
    generic_errors()

    for t in threads:
        t.join()

    print("Program exited with code 139", file=sys.stderr)

if __name__ == "__main__":
    main()
