#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modify DATM XML stream files for eCLM runs.

Uses lxml for structured XML modification (preferred over regex
because stream files are nested XML whose elements span multiple lines
with varying indentation).

Usage example:
    python modify_stream_files.py \\
        --rundir ../namelist_eCLM_bgcmode-template \\
        --file user_datm.streams.txt.CLMCRUNCEPv7.Solar \\
        --domaininfo-filepath ./input_clm \\
        --domaininfo-filenames domain.lnd.DE-RuS.240717.nc \\
        --fieldinfo-filepath ./forcings \\
        --fieldinfo-filenames "2022-01.nc\\n2022-02.nc\\n2022-03.nc"

Newlines in values:
    Use the escape sequence \\n in any value to insert a real newline in
    the output, e.g. for multi-file <fileNames> entries.
"""
import argparse
import os
import shlex
import sys
from io import BytesIO

from lxml import etree


# Maps argparse dest names to XPath expressions inside the stream file root.
_XPATH_MAP = {
    "datasource":               "dataSource",
    "domaininfo_filepath":      "domainInfo/filePath",
    "domaininfo_filenames":     "domainInfo/fileNames",
    "domaininfo_variablenames": "domainInfo/variableNames",
    "fieldinfo_filepath":       "fieldInfo/filePath",
    "fieldinfo_filenames":      "fieldInfo/fileNames",
    "fieldinfo_variablenames":  "fieldInfo/variableNames",
    "fieldinfo_offset":         "fieldInfo/offset",
}


def _set_element_text(root, xpath, new_text):
    """Set the text of the first element matched by xpath.

    The surrounding whitespace (indentation before the content, trailing
    newline/indent before the closing tag) is preserved from the original
    element text so that the file formatting is not disturbed.
    """
    elements = root.xpath(xpath)
    if not elements:
        return False
    el = elements[0]
    old = el.text or ""
    stripped = old.strip()
    if stripped:
        prefix = old[: len(old) - len(old.lstrip())]
        suffix = old[len(old.rstrip()):]
        # For multi-line values, reduce the prefix to a bare newline so that
        # placeholder indentation (e.g. a tab before __forclist__) does not
        # carry over to the first line of the new value.
        if "\n" in new_text:
            prefix = prefix.rstrip(" \t") or "\n"
    else:
        # Element was empty — use a reasonable default indent
        prefix = "\n      "
        suffix = "\n   "
    el.text = prefix + new_text + suffix
    return True


def modify_stream_file(path, **kwargs):
    """Modify a single XML stream file in-place.

    kwargs keys correspond to _XPATH_MAP entries; None values are skipped.
    """
    # Preserve the original XML declaration (some files have encoding=,
    # others do not).
    with open(path, "r", encoding="utf-8") as fh:
        first_line = fh.readline()
    original_decl = first_line.rstrip("\n") if first_line.startswith("<?xml") else None

    tree = etree.parse(path)
    root = tree.getroot()

    for key, value in kwargs.items():
        if value is None:
            continue
        xpath = _XPATH_MAP.get(key)
        if xpath is None:
            continue
        _set_element_text(root, xpath, value)

    # Serialise via a byte buffer so we can control the declaration.
    fbuffer = BytesIO()
    tree.write(fbuffer, xml_declaration=True, encoding="UTF-8")
    fstr = fbuffer.getvalue().decode("utf-8")

    # Strip lxml's generated declaration and restore the original one.
    if fstr.startswith("<?xml"):
        fstr = fstr[fstr.index("?>") + 2:].lstrip("\n")
    if original_decl is not None:
        fstr = original_decl + "\n" + fstr

    if not fstr.endswith("\n"):
        fstr += "\n"

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(fstr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Modify DATM XML stream files for eCLM runs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-r", "--rundir",
        default=".",
        help="Directory containing the stream files to modify (default: current directory)",
    )
    parser.add_argument(
        "-f", "--file",
        nargs="+",
        required=True,
        metavar="STREAMFILE",
        help="Stream file(s) to modify (filenames relative to --rundir)",
    )

    group_domaininfo = parser.add_argument_group(
        "domaininfo", "stream file <domainInfo> section"
    )
    group_domaininfo.add_argument(
        "--domaininfo-filepath", type=str, default=None,
        help="<domainInfo><filePath> — directory of the domain file",
    )
    group_domaininfo.add_argument(
        "--domaininfo-filenames", type=str, default=None,
        help="<domainInfo><fileNames> — domain filename(s), use \\n to separate multiple",
    )
    group_domaininfo.add_argument(
        "--domaininfo-variablenames", type=str, default=None,
        help="<domainInfo><variableNames> — variable name mapping pairs",
    )

    group_fieldinfo = parser.add_argument_group(
        "fieldinfo", "stream file <fieldInfo> section"
    )
    group_fieldinfo.add_argument(
        "--fieldinfo-filepath", type=str, default=None,
        help="<fieldInfo><filePath> — directory of the forcing/field files",
    )
    group_fieldinfo.add_argument(
        "--fieldinfo-filenames", type=str, default=None,
        help="<fieldInfo><fileNames> — field filename(s), use \\n to separate multiple",
    )
    group_fieldinfo.add_argument(
        "--fieldinfo-variablenames", type=str, default=None,
        help="<fieldInfo><variableNames> — variable name mapping pairs",
    )
    group_fieldinfo.add_argument(
        "--fieldinfo-offset", type=str, default=None,
        help="<fieldInfo><offset>",
    )

    parser.add_argument(
        "--datasource", type=str, default=None,
        help="<dataSource> text content",
    )

    args = parser.parse_args()

    # Expand \n escapes in all string values (same convention as
    # modify_case_namelists.py).
    kwargs = {
        k: v.replace("\\n", "\n") if isinstance(v, str) else v
        for k, v in vars(args).items()
        if k in _XPATH_MAP
    }

    for filename in args.file:
        path = os.path.join(args.rundir, filename)
        modify_stream_file(path, **kwargs)
