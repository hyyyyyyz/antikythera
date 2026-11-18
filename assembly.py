"""Generate an animated, self-contained SVG assembly calendar."""

import argparse
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from board import render
from calendar_data import daily_commits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", required=True)
    parser.add_argument("--output", type=Path, default=Path("assembly-log.svg"))
    parser.add_argument("--compact-output", type=Path, help="Optional portrait SVG with two calendar bands")
    args = parser.parse_args()
    if args.compact_output and args.output.resolve() == args.compact_output.resolve():
        parser.error("the regular and compact outputs need different file paths")
    end = datetime.now(timezone.utc).date()
    counts = daily_commits(args.username, end - timedelta(days=364), end)
    drawings = [(args.output, render(args.username, end, counts))]
    if args.compact_output:
        drawings.append((args.compact_output, render(args.username, end, counts, compact=True)))
    for output, drawing in drawings:
        output.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent, delete=False) as temp:
            temp.write(drawing)
        os.replace(temp.name, output)
    print(f"Wrote {args.output} with {sum(counts.values()):,} public commit contributions.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError) as error:
        sys.exit(str(error))
