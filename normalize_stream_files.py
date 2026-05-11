#!/usr/bin/env python3
"""
normalize_stream_files.py - Unify style in eCLM DATM stream XML files.

Applies one transformation to eCLM DATM stream files (datm.streams.*):

  1. Indentation is set to exactly two spaces per nesting level.  The XML
     declaration (<?xml ... ?>) and the root element (<file ...>) are kept
     at column 0.  Every child element and every text-content line is
     re-indented to reflect its depth in the element tree.

Usage
-----
  # Normalize all stream files in the current directory
  python3 normalize_stream_files.py

  # Normalize stream files in a specific run directory
  python3 normalize_stream_files.py /path/to/rundir

  # Preview which files would change without writing anything
  python3 normalize_stream_files.py --dry-run [rundir]
"""
import argparse
import glob
import os
import re


def normalize_content(content):
    """Return *content* with unified two-spaces-per-level indentation.

    The function processes the file line by line, tracking the current
    element depth.

    Opening tags increment the depth *after* they are written; closing
    tags decrement the depth *before* they are written.

    Text content lines are indented at the current depth. Empty lines
    are passed through unchanged. Self-closing tags (<tag/>) do not
    change the depth.
    """
    lines = content.splitlines(keepends=True)
    result = []
    depth = 0

    for line in lines:
        nl = "\n" if line.endswith("\n") else ""
        stripped = line.strip()

        if not stripped:
            result.append(nl)
            continue

        # XML declaration: <?xml ... ?>
        if stripped.startswith("<?"):
            result.append(stripped + nl)
            continue

        # Closing tag: </tag>
        if stripped.startswith("</"):
            depth -= 1
            result.append("  " * depth + stripped + nl)
            continue

        # Self-closing tag: <tag ... />
        if re.match(r"<[^/][^>]*/\s*>", stripped):
            result.append("  " * depth + stripped + nl)
            continue

        # Opening tag: <tag ...>
        if stripped.startswith("<"):
            result.append("  " * depth + stripped + nl)
            depth += 1
            continue

        # Text content line
        result.append("  " * depth + stripped + nl)

    return "".join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "rundir",
        nargs="?",
        default=".",
        help="Directory containing stream files (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would change without writing",
    )
    args = parser.parse_args()

    pattern = os.path.join(args.rundir, "datm.streams.*")
    paths = sorted(glob.glob(pattern))

    if not paths:
        print("No datm.streams.* files found.")
        return

    for path in paths:
        if not os.path.isfile(path):
            continue
        filename = os.path.basename(path)
        with open(path) as fh:
            original = fh.read()
        normalized = normalize_content(original)
        if normalized == original:
            print(f"{filename}: no changes")
            continue
        if args.dry_run:
            print(f"{filename}: would be modified")
        else:
            with open(path, "w") as fh:
                fh.write(normalized)
            print(f"{filename}: normalized")


if __name__ == "__main__":
    main()
