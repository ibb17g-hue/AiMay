"""
AiMay — точка входу.

Використання:
    python main.py examples/hello_intent.aim
    python main.py          (запускає всі приклади з examples/)
"""

import sys
import os
from engine.core import AiMayEngine

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")


def run_all_examples():
    engine = AiMayEngine(seed=42)
    engine._print_header("усі приклади з examples/")
    for fname in sorted(os.listdir(EXAMPLES_DIR)):
        if not fname.endswith(".aim"):
            continue
        with open(os.path.join(EXAMPLES_DIR, fname), encoding="utf-8") as f:
            source = f.read()
        engine.run_source(source, header=fname)
    engine._print_summary()


def main():
    if len(sys.argv) > 1:
        engine = AiMayEngine(seed=42)
        engine.run_file(sys.argv[1])
    else:
        run_all_examples()


if __name__ == "__main__":
    main()
