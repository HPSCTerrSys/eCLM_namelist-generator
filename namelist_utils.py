#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re


def _set_nml_value(content, key, value):
    """Replace a namelist key's value, converting Python types to Fortran."""
    if isinstance(value, bool):
        value = ".true." if value else ".false."
    return _re_set_value(content, key, value)


def _re_set_value(content, key, value):
    """Replace a single namelist key's value using regexp.

    Tries a quoted match first to preserve the existing quote character
    (single or double).  Falls back to a bare-token match for unquoted
    numeric values.  The key match is case-insensitive and tolerates
    surrounding whitespace.
    """
    value = str(value)
    # Try quoted match first — preserves the existing quote character.
    # Also strips any trailing whitespace/comment after the closing quote.
    new_content, count = re.subn(
        rf"(\b{re.escape(key)}\s*=\s*)(['\"])[^'\"]*\2[ \t]*(?:!.*)?",
        lambda m: m.group(1) + m.group(2) + value + m.group(2),
        content, flags=re.IGNORECASE,
    )
    if count > 0:
        return new_content
    # Fall back to unquoted (bare numeric/logical) match.
    # Also strips any trailing whitespace/comment after the value token.
    return re.sub(
        rf"(\b{re.escape(key)}\s*=\s*)\S+[ \t]*(?:!.*)?",
        rf"\g<1>{value}",
        content, flags=re.IGNORECASE,
    )


def _re_set_multivalue(content, key, value):
    """Replace a namelist value that may span multiple lines.

    Matches everything from 'key =' up to (but not including) the line
    that starts the next key assignment or the group-closing slash.
    The replacement value is inserted verbatim, so the caller is
    responsible for formatting (quoting, commas, etc.).
    """
    pattern = rf"(\b{re.escape(key)}\s*=\s*)(.*?)(?=\n\s*(?:\w+\s*=|/))"
    return re.sub(
        pattern,
        lambda m: m.group(1) + str(value),
        content, flags=re.DOTALL | re.IGNORECASE,
    )


def _re_add_ens_suffix(content, key, iens, pad=4):
    """Insert _NNNN before the file extension of a namelist string value.

    For example, with key='logfile' and iens=3, 'run.log' becomes 'run_0003.log'.
    pad controls the zero-padding width of the ensemble index (default: 4).
    """
    suffix = "_" + str(iens).zfill(pad)

    def replacer(m):
        base, ext = os.path.splitext(m.group(2))
        return m.group(1) + base + suffix + ext + m.group(3)

    pattern = rf"(\b{re.escape(key)}\s*=\s*['\"])([^'\"]+)(['\"])"
    return re.sub(pattern, replacer, content, flags=re.IGNORECASE)


def _re_add_ens_suffix_after_clm2(content, key, iens, pad=4):
    """Insert _NNNN after '.clm2' in a namelist string value.

    For finidat files like 'case.clm2.r.DATE.nc', inserts the suffix
    immediately after '.clm2': 'case.clm2_0001.r.DATE.nc'.
    pad controls the zero-padding width of the ensemble index (default: 4).
    """
    suffix = "_" + str(iens).zfill(pad)

    def replacer(m):
        new_val = re.sub(r"(\.clm2)(\W)", r"\g<1>" + suffix + r"\2", m.group(2))
        return m.group(1) + new_val + m.group(3)

    pattern = rf"(\b{re.escape(key)}\s*=\s*['\"])([^'\"]+)(['\"])"
    return re.sub(pattern, replacer, content, flags=re.IGNORECASE)


def _re_get_streams_filenames(filename):
    """Extract stream file paths (first word of each quoted streams entry)."""
    with open(filename, "r") as fh:
        content = fh.read()
    m = re.search(
        r"\bstreams\s*=\s*(.*?)(?=\n[ \t]*[a-zA-Z_]|\Z)", content,
        re.DOTALL | re.IGNORECASE,
    )
    if m is None:
        return []
    streams_block = m.group(1)
    return [entry.split()[0] for entry in re.findall(r"['\"]([^'\"]+)['\"]", streams_block)]
