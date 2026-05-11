#!/usr/bin/env python3
"""
normalize_namelists.py - Unify style in eCLM-PDAF namelist files.

Applies two transformations to eCLM namelist files (drv_flds_in,
drv_in, lnd_in, datm_in, mosart_in, and the *_modelio.nml files):

  1. Indentation inside namelist groups (&group ... /) is set to exactly
     two spaces.  Group header lines (&group) and closing slashes (/) are
     left as-is.

  2. String values delimited by double quotes are rewritten to use single
     quotes.  The value content itself is never modified, only the delimiter
     characters change ("value" -> 'value').

  3. Continuation lines of multi-line values are indented to align with the
     value start on the key = value line above (one space after the = sign),
     e.g.:
       hist_fincl1 = 'SOILWATER_10CM', 'H2OSOI',
                     'SOILLIQ', 'SOILICE'

Usage
-----
  # Normalize all namelist files in the current directory
  python3 normalize_namelists.py

  # Normalize files in a specific run directory
  python3 normalize_namelists.py /path/to/rundir

  # Preview which files would change without writing anything
  python3 normalize_namelists.py --dry-run [rundir]
"""
import argparse
import os
import re

_MODELIO_COMPONENTS = ("atm", "cpl", "esp", "glc", "ice", "lnd", "ocn", "rof", "wav")
_NAMELIST_FILES = [
    "drv_flds_in",
    "drv_in",
    "lnd_in",
    "datm_in",
    "mosart_in",
] + [f"{c}_modelio.nml" for c in _MODELIO_COMPONENTS]


def normalize_content(content):
    """Return *content* with unified indentation and single-quoted string values.

    The function processes the file line by line, tracking whether the current
    position is inside a namelist group.  Only lines inside a group are
    modified; everything else (blank lines, trailing comment blocks added by
    modify_case_namelists.py, etc.) is passed through unchanged.
    """
    lines = content.splitlines(keepends=True)
    result = []
    in_group = False
    continuation_indent = "  "  # updated each time a new key = value line is seen
    for line in lines:
        nl = "\n" if line.endswith("\n") else ""
        stripped = line.rstrip("\n")

        # A line starting with & followed by a word character opens a group.
        if re.match(r"^\s*&\w", stripped):
            in_group = True
            continuation_indent = "  "
            result.append(line)
            continue

        # A line whose first non-space character is / closes the group.
        if re.match(r"^\s*/", stripped):
            in_group = False
            result.append(line)
            continue

        if in_group and stripped.strip():
            # Strip existing indentation and re-apply exactly two spaces.
            body = stripped.lstrip()
            # Replace double-quoted strings with single-quoted ones.
            # The capture group preserves the value content verbatim so that
            # only the delimiter characters are changed, never the value itself.
            body = re.sub(r'"([^"]*)"', lambda m: "'" + m.group(1) + "'", body)

            m = re.match(r"(\w+\s*=\s*)", body)
            if m:
                # Key = value line: record where the value starts so that
                # continuation lines can be aligned with it.
                continuation_indent = " " * (2 + len(m.group(1)))
                result.append("  " + body + nl)
            elif body.startswith("!"):
                # Comment line: not a continuation, reset continuation indent.
                continuation_indent = "  "
                result.append("  " + body + nl)
            else:
                # Continuation line of a multi-line value: indent to align
                # with the value start on the key = value line above.
                result.append(continuation_indent + body + nl)
        else:
            # Empty lines inside a group and all lines outside a group are
            # left untouched.
            result.append(line)

    return "".join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "rundir",
        nargs="?",
        default=".",
        help="Directory containing namelist files (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would change without writing",
    )
    args = parser.parse_args()

    for filename in _NAMELIST_FILES:
        path = os.path.join(args.rundir, filename)
        if not os.path.isfile(path):
            continue
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
