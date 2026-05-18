#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create per-ensemble-member namelist files for eCLM-PDAF runs.

For each ensemble member 1..N, writes ensemble-specific copies of:
  - <mod>_modelio.nml_NNNN  (atm, esp, glc, ice, lnd, ocn, rof, wav, cpl)
  - datm_in_NNNN
  - lnd_in_NNNN
  - mosart_in_NNNN
  - datm.streams_NNNN.*     (XML stream description files)

Usage
-----
    python create_ensemble_namelists.py [OPTIONS]

Options
-------
  -r, --rundir DIR          Run directory containing the base namelists (default: .)
  -n, --num_ensemble INT    Number of ensemble members (default: 96)
  -b, --backend BACKEND     Namelist backend: 're' (default) or 'f90nml'
  -f, --forcings-dir DIR    Forcings directory in stream files (default: ./forcings)
  --suffix-fsurdat          Add ensemble suffix to clm_inparm:fsurdat in lnd_in
"""
import argparse
import os
import sys

import f90nml
from lxml import etree
from io import BytesIO

from namelist_utils import _re_add_ens_suffix, _re_get_streams_filenames


def adapt_modelio(mod, iens, backend="re"):
    """Write <mod>_modelio.nml_NNNN from <mod>_modelio.nml.

    Changes: logfile gets an ensemble suffix (_NNNN) inserted before the
    file extension, e.g. 'lnd.log' -> 'lnd_0003.log'.
    """
    if backend == "f90nml":
        nml = f90nml.read(mod + "_modelio.nml")
        nml.indent = 1

        nml["modelio"]["logfile"] = nml["modelio"]["logfile"].replace(
            ".log", "_" + str(iens).zfill(4) + ".log")

        nml.write(mod + "_modelio.nml_" + str(iens).zfill(4))

    elif backend == "re":
        with open(mod + "_modelio.nml", "r") as fh:
            content = fh.read()

        content = _re_add_ens_suffix(content, "logfile", iens)

        with open(mod + "_modelio.nml_" + str(iens).zfill(4), "w") as fh:
            fh.write(content)


def adapt_mosart_in(iens, backend="re"):
    """Write mosart_in_NNNN from mosart_in (unchanged copy)."""
    if backend == "f90nml":
        nml = f90nml.read("mosart_in")
        nml.indent = 1
        nml.write("mosart_in_" + str(iens).zfill(4))

    elif backend == "re":
        with open("mosart_in", "r") as fh:
            content = fh.read()
        with open("mosart_in_" + str(iens).zfill(4), "w") as fh:
            fh.write(content)


def adapt_datm_in(iens, backend="re"):
    """Write datm_in_NNNN from datm_in.

    Changes:

    Each entry in shr_strdata_nml:streams gets an ensemble suffix
    inserted before the first '.txt' in the filename, e.g.
    'datm.streams.txt.CLMCRUNCEPv7.Solar' ->
    'datm.streams_0003.txt.CLMCRUNCEPv7.Solar'.

    """
    if backend == "f90nml":
        nml = f90nml.read("datm_in")
        nml.indent = 1

        for i, streamfile in enumerate(nml["shr_strdata_nml"]["streams"]):
            nml["shr_strdata_nml"]["streams"][i] = streamfile.replace(
                ".txt", "_" + str(iens).zfill(4) + ".txt")

        nml.write("datm_in_" + str(iens).zfill(4))

    elif backend == "re":
        with open("datm_in", "r") as fh:
            content = fh.read()

        for sf in _re_get_streams_filenames("datm_in"):
            ens_sf = sf.replace(".txt", "_" + str(iens).zfill(4) + ".txt", 1)
            content = content.replace(sf, ens_sf)

        with open("datm_in_" + str(iens).zfill(4), "w") as fh:
            fh.write(content)


def adapt_lnd_in(iens, suffix_fsurdat=False, backend="re"):
    """Write lnd_in_NNNN from lnd_in.

    If suffix_fsurdat is True, clm_inparm:fsurdat gets an ensemble suffix
    inserted before the file extension, e.g. 'surfdata.nc' -> 'surfdata_00003.nc'
    (zero-padded to 5 digits). Otherwise lnd_in_NNNN is an unchanged copy.
    """
    if backend == "f90nml":
        nml = f90nml.read("lnd_in")
        nml.indent = 1

        if suffix_fsurdat:
            nml["clm_inparm"]["fsurdat"] = nml["clm_inparm"]["fsurdat"].replace(
                ".nc", "_" + str(iens).zfill(5) + ".nc")

        nml.write("lnd_in_" + str(iens).zfill(4))

    elif backend == "re":
        with open("lnd_in", "r") as fh:
            content = fh.read()
        if suffix_fsurdat:
            content = _re_add_ens_suffix(content, "fsurdat", iens, pad=5)
        with open("lnd_in_" + str(iens).zfill(4), "w") as fh:
            fh.write(content)


def adapt_stream_files(iens, forcings_dir="./forcings", backend="re"):
    """Write per-ensemble XML stream description files.

    Must be called after adapt_datm_in, which determines the ensemble
    stream filenames.

    For each stream file listed in datm_in, reads the original XML and
    writes an ensemble-specific copy (named as in datm_in_NNNN), with
    the fieldInfo/filePath entries under forcings_dir redirected to
    '<forcings_dir>/real_NNNNN'.

    """
    # Must be called after datm update

    if backend == "f90nml":
        # Read original stream files and new stream files
        nml_datm = f90nml.read("datm_in")
        nml_datm_ens = f90nml.read("datm_in_" + str(iens).zfill(4))

        orig_streamfiles = nml_datm["shr_strdata_nml"]["streams"]
        ens_streamfiles = nml_datm_ens["shr_strdata_nml"]["streams"]

    elif backend == "re":
        orig_streamfiles = _re_get_streams_filenames("datm_in")
        ens_streamfiles = _re_get_streams_filenames("datm_in_" + str(iens).zfill(4))

    for orig, ens_sf in zip(orig_streamfiles, ens_streamfiles):
        orig_path = orig.split()[0] if backend == "f90nml" else orig
        ens_path = ens_sf.split()[0] if backend == "f90nml" else ens_sf

        tree = etree.parse(orig_path)
        root = tree.getroot()

        # Extract element "filePath" with parent element "fieldInfo"
        for filePath in root.iter("filePath"):
            # Check parent
            if filePath.getparent().tag == "fieldInfo":
                # print(filePath.getparent().tag, filePath.tag)
                if filePath.text.find(forcings_dir) > -1:
                    filePath.text = filePath.text.replace(
                        forcings_dir, forcings_dir + "/real_" + str(iens).zfill(5)
                    )

        # Write XML streamfile
        # --------------------

        # Use buffer first
        fbuffer = BytesIO()
        tree.write(fbuffer, xml_declaration=True, encoding="ASCII")
        fstr = fbuffer.getvalue().decode("ASCII")

        # Replace XML declaration to match original
        fstr = fstr.replace("version='1.0'", 'version="1.0"')
        fstr = fstr.replace(" encoding='ASCII'", "")

        # Write to file
        with open(ens_path, "w+") as f:
            f.write(fstr)


def create_ensemble_namelists(iens, suffix_fsurdat=False, forcings_dir="./forcings", backend="re"):
    """Create all per-ensemble namelist files for ensemble member iens.

    Calls:

    - adapt_modelio for all nine CIME components (atm, esp, glc, ice,
    lnd, ocn, rof, wav, cpl)
    - adapt_datm_in
    - adapt_lnd_in
    - adapt_mosart_in
    - adapt_stream_files
    """
    for m in ["atm", "esp", "glc", "ice", "lnd", "ocn", "rof", "wav", "cpl"]:
        adapt_modelio(m, iens, backend=backend)

    adapt_datm_in(iens, backend=backend)

    adapt_lnd_in(iens, suffix_fsurdat=suffix_fsurdat, backend=backend)

    adapt_mosart_in(iens, backend=backend)

    adapt_stream_files(iens, forcings_dir=forcings_dir, backend=backend)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create ensemble namelists for eCLM-PDAF runs"
    )
    parser.add_argument(
        "-r", "--rundir",
        default=".",
        help="Run directory containing the base namelists (default: current directory)",
    )
    parser.add_argument(
        "-n", "--num_ensemble",
        type=int,
        default=96,
        help="Number of ensemble members (default: 96)",
    )
    parser.add_argument(
        "-b", "--backend",
        choices=["f90nml", "re"],
        default="re",
        help="Backend for reading/writing namelists: 're' (default, regexp) or 'f90nml'",
    )
    parser.add_argument(
        "-f", "--forcings-dir",
        default="./forcings",
        help="Forcings directory used in stream file filePath entries (default: ./forcings)",
    )
    parser.add_argument(
        "--suffix-fsurdat",
        action="store_true",
        default=False,
        help="Add ensemble suffix to clm_inparm:fsurdat in lnd_in (default: off)",
    )

    args = parser.parse_args()

    os.chdir(args.rundir)

    for ens in range(1, args.num_ensemble + 1):
        create_ensemble_namelists(ens, suffix_fsurdat=args.suffix_fsurdat,
                                  forcings_dir=args.forcings_dir, backend=args.backend)
        sys.stdout.write("\r[%s] " % ("Done with ensemble member: " + str(ens)))
        sys.stdout.flush()

    sys.stdout.write("\n")
    sys.stdout.flush()
