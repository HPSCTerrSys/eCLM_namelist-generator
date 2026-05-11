#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import os
import datetime
import shlex

import f90nml
from lxml import etree
from io import BytesIO

from namelist_utils import _re_set_multivalue, _re_set_value, _set_nml_value


def _append_modification_comment(filename):
    cmd = " ".join(shlex.quote(a) for a in sys.argv)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comment = (
        "\n!#--------------------------------------------------------------------------------------------------------------------------\n"
        f"!# {filename}:: Modified by modify_case_namelists.py on {timestamp}\n"
        f"!# Command: {cmd}\n"
        "!#--------------------------------------------------------------------------------------------------------------------------\n"
    )
    with open(filename, "a") as fh:
        fh.write(comment)


_MODELIO_PREFIX_GROUP = {
    "modelio_": "modelio",
    "pio_inparm_": "pio_inparm",
}

_MODELIO_COMPONENTS = ("atm", "cpl", "esp", "glc", "ice", "lnd", "ocn", "rof", "wav")
_MODELIO_FILES = tuple(f"{c}_modelio.nml" for c in _MODELIO_COMPONENTS)


def adapt_modelio(filename, backend="re", rundir=".", changelog=True, **kwargs):
    path = os.path.join(rundir, filename)
    if backend == "f90nml":
        nml = f90nml.read(path)
        nml.indent = 1
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix, group in _MODELIO_PREFIX_GROUP.items():
                if key.startswith(prefix):
                    nml[group][key[len(prefix):]] = value
                    break
        nml.write(path, force=True)

    elif backend == "re":
        with open(path, "r") as fh:
            content = fh.read()
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix in _MODELIO_PREFIX_GROUP:
                if key.startswith(prefix):
                    content = _set_nml_value(content, key[len(prefix):], value)
                    break
        with open(path, "w") as fh:
            fh.write(content)
    if changelog:
        _append_modification_comment(path)


_DRV_FLDS_IN_PREFIX_GROUP = {
    "megan_": "megan_emis_nl",
}

# megan_specifier spans multiple comma-separated / multi-line tokens
_DRV_FLDS_IN_MULTIVALUE = {
    "megan_specifier",
}


def adapt_drv_flds_in(backend="re", rundir=".", changelog=True, **kwargs):
    path = os.path.join(rundir, "drv_flds_in")
    if backend == "f90nml":
        nml = f90nml.read(path)
        nml.indent = 1
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix, group in _DRV_FLDS_IN_PREFIX_GROUP.items():
                if key.startswith(prefix):
                    nml[group][key[len(prefix):]] = value
                    break
        nml.write(path, force=True)

    elif backend == "re":
        with open(path, "r") as fh:
            content = fh.read()
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix in _DRV_FLDS_IN_PREFIX_GROUP:
                if key.startswith(prefix):
                    nml_key = key[len(prefix):]
                    if nml_key in _DRV_FLDS_IN_MULTIVALUE:
                        content = _re_set_multivalue(content, nml_key, value)
                    else:
                        content = _set_nml_value(content, nml_key, value)
                    break
        with open(path, "w") as fh:
            fh.write(content)
    if changelog:
        _append_modification_comment(path)


_DRV_IN_PREFIX_GROUP = {
    "timemgr_": "seq_timemgr_inparm",
    "infodata_": "seq_infodata_inparm",
    "driver_": "cime_driver_inst",
    "pes_": "cime_pes",
    "esmf_": "esmf_inparm",
    "papi_": "papi_inparm",
    "pio_": "pio_default_inparm",
    "prof_": "prof_inparm",
    "cplflds_": "seq_cplflds_inparm",
    "cplcustom_": "seq_cplflds_userspec",
    "flux_mct_": "seq_flux_mct_inparm",
}


def adapt_drv_in(backend="re", rundir=".", changelog=True, **kwargs):
    path = os.path.join(rundir, "drv_in")
    if backend == "f90nml":
        nml = f90nml.read(path)
        nml.indent = 1
        nml["seq_infodata_inparm"]["username"] = os.environ.get("USER", "unknown")
        nml["seq_infodata_inparm"]["hostname"] = os.environ.get(
            "SYSTEMNAME", os.environ.get("CPUNAME", "unknown")
        ).upper()
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix, group in _DRV_IN_PREFIX_GROUP.items():
                if key.startswith(prefix):
                    nml[group][key[len(prefix):]] = value
                    break
        nml.write(path, force=True)

    elif backend == "re":
        with open(path, "r") as fh:
            content = fh.read()
        content = _re_set_value(
            content, "username",
            kwargs.pop("infodata_username", None) or os.environ.get("USER", "unknown"),
        )
        content = _re_set_value(
            content, "hostname",
            kwargs.pop("infodata_hostname", None) or os.environ.get("SYSTEMNAME", os.environ.get("CPUNAME", "unknown")).upper(),
        )
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix in _DRV_IN_PREFIX_GROUP:
                if key.startswith(prefix):
                    content = _set_nml_value(content, key[len(prefix):], value)
                    break
        with open(path, "w") as fh:
            fh.write(content)
    if changelog:
        _append_modification_comment(path)




_LND_IN_PREFIX_GROUP = {
    "clm_inparm_": "clm_inparm",
    "ndepdyn_": "ndepdyn_nml",
    "popd_": "popd_streams",
    "urbantv_": "urbantv_streams",
    "light_": "light_streams",
    "atm2lnd_": "atm2lnd_inparm",
    "lnd2atm_": "lnd2atm_inparm",
    "canopyhydro_": "clm_canopyhydrology_inparm",
    "cnphenology_": "cnphenology",
    "cnvegcarbon_": "cnvegcarbonstate",
    "century_": "century_soilbgcdecompcascade",
    "soilhydro_": "soilhydrology_inparm",
    "luna_": "luna",
    "friction_": "friction_velocity",
    "soilwater_": "soilwater_movement_inparm",
    "rooting_": "rooting_profile_inparm",
    "soil_resis_": "soil_resis_inparm",
    "bgc_shared_": "bgc_shared",
    "canopyflux_": "canopyfluxes_inparm",
    "aerosol_": "aerosol",
    "clmu_": "clmu_inparm",
    "clm_soilstate_": "clm_soilstate_inparm",
    "clm_nitrogen_": "clm_nitrogen",
    "clm_snowhydro_": "clm_snowhydrology_inparm",
    "cnprecision_": "cnprecision_inparm",
    "glacier_": "clm_glacier_behavior",
    "crop_": "crop",
    "irrigation_": "irrigation_inparm",
    "ch4finundated_": "ch4finundated",
    "ch4_": "ch4par_in",
    "humanindex_": "clm_humanindex_inparm",
    "cnmresp_": "cnmresp_inparm",
    "photosyns_": "photosyns_inparm",
    "cnfire_": "cnfire_inparm",
    "cn_general_": "cn_general",
    "lifire_": "lifire_inparm",
    "clm_canopy_": "clm_canopy_inparm",
}

# Keys whose value spans multiple comma-separated tokens (replace whole value until EOL//)
_LND_IN_MULTIVALUE = {
    "albice",
    "hist_fincl1",
    "initial_cstocks",
    "glacier_region_behavior",
    "glacier_region_ice_runoff_behavior",
    "glacier_region_melt_behavior",
    "glacier_region_rain_to_snow_behavior",
    "cmb_cmplt_fact",
}


def adapt_lnd_in(backend="re", rundir=".", changelog=True, **kwargs):
    path = os.path.join(rundir, "lnd_in")
    if backend == "f90nml":
        nml = f90nml.read(path)
        nml.indent = 1
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix, group in _LND_IN_PREFIX_GROUP.items():
                if key.startswith(prefix):
                    nml[group][key[len(prefix):]] = value
                    break
        nml.write(path, force=True)

    elif backend == "re":
        with open(path, "r") as fh:
            content = fh.read()
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix in _LND_IN_PREFIX_GROUP:
                if key.startswith(prefix):
                    nml_key = key[len(prefix):]
                    if nml_key in _LND_IN_MULTIVALUE:
                        content = _re_set_multivalue(content, nml_key, value)
                    else:
                        content = _set_nml_value(content, nml_key, value)
                    break
        with open(path, "w") as fh:
            fh.write(content)
    if changelog:
        _append_modification_comment(path)



_DATM_IN_PREFIX_GROUP = {
    "datm_nml_": "datm_nml",
    "shr_strdata_nml_": "shr_strdata_nml",
}

# Keys in shr_strdata_nml whose value is a comma-separated list of tokens
_DATM_IN_MULTIVALUE = {
    "streams",
    "dtlimit",
    "fillalgo",
    "fillmask",
    "fillread",
    "fillwrite",
    "mapalgo",
    "mapmask",
    "mapread",
    "mapwrite",
    "readmode",
    "taxmode",
    "tintalgo",
}


def adapt_datm_in(backend="re", rundir=".", changelog=True, **kwargs):
    path = os.path.join(rundir, "datm_in")
    if backend == "f90nml":
        nml = f90nml.read(path)
        nml.indent = 1
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix, group in _DATM_IN_PREFIX_GROUP.items():
                if key.startswith(prefix):
                    nml[group][key[len(prefix):]] = value
                    break
        nml.write(path, force=True)

    elif backend == "re":
        with open(path, "r") as fh:
            content = fh.read()
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix in _DATM_IN_PREFIX_GROUP:
                if key.startswith(prefix):
                    nml_key = key[len(prefix):]
                    if nml_key in _DATM_IN_MULTIVALUE:
                        content = _re_set_multivalue(content, nml_key, value)
                    else:
                        content = _set_nml_value(content, nml_key, value)
                    break
        with open(path, "w") as fh:
            fh.write(content)
    if changelog:
        _append_modification_comment(path)


_MOSART_IN_PREFIX_GROUP = {
    "mosart_inparm_": "mosart_inparm",
}

# History include/exclude field lists — can be comma-separated multi-token values
_MOSART_IN_MULTIVALUE = {
    "rtmhist_fincl1",
    "rtmhist_fincl2",
    "rtmhist_fincl3",
    "rtmhist_fexcl1",
    "rtmhist_fexcl2",
    "rtmhist_fexcl3",
}


def adapt_mosart_in(backend="re", rundir=".", changelog=True, **kwargs):
    path = os.path.join(rundir, "mosart_in")
    if backend == "f90nml":
        nml = f90nml.read(path)
        nml.indent = 1
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix, group in _MOSART_IN_PREFIX_GROUP.items():
                if key.startswith(prefix):
                    nml[group][key[len(prefix):]] = value
                    break
        nml.write(path, force=True)

    elif backend == "re":
        with open(path, "r") as fh:
            content = fh.read()
        for key, value in kwargs.items():
            if value is None:
                continue
            for prefix in _MOSART_IN_PREFIX_GROUP:
                if key.startswith(prefix):
                    nml_key = key[len(prefix):]
                    if nml_key in _MOSART_IN_MULTIVALUE:
                        content = _re_set_multivalue(content, nml_key, value)
                    else:
                        content = _set_nml_value(content, nml_key, value)
                    break
        with open(path, "w") as fh:
            fh.write(content)
    if changelog:
        _append_modification_comment(path)



_DRV_FLDS_IN_PREFIXES = tuple(_DRV_FLDS_IN_PREFIX_GROUP.keys())
_DRV_IN_PREFIXES = tuple(_DRV_IN_PREFIX_GROUP.keys())
_LND_IN_PREFIXES = tuple(_LND_IN_PREFIX_GROUP.keys())
_DATM_IN_PREFIXES = tuple(_DATM_IN_PREFIX_GROUP.keys())
_MOSART_IN_PREFIXES = tuple(_MOSART_IN_PREFIX_GROUP.keys())
_MODELIO_PREFIXES = tuple(_MODELIO_PREFIX_GROUP.keys())


def modify_case_namelists(adapt=None, backend="re", rundir=".", changelog=True, **kwargs):
    """
    Modify case configuration files for a single case.
    rundir specifies the directory containing the namelist files to modify.
    """
    if adapt is None:
        adapt = ["drv_flds_in", "drv_in", "lnd_in", "datm_in", "mosart_in"]
    if "drv_flds_in" in adapt:
        adapt_drv_flds_in(
            backend=backend, rundir=rundir, changelog=changelog,
            **{k: v for k, v in kwargs.items() if k.startswith(_DRV_FLDS_IN_PREFIXES)},
        )
    if "drv_in" in adapt:
        adapt_drv_in(
            backend=backend, rundir=rundir, changelog=changelog,
            **{k: v for k, v in kwargs.items() if k.startswith(_DRV_IN_PREFIXES)},
        )
    if "lnd_in" in adapt:
        adapt_lnd_in(
            backend=backend, rundir=rundir, changelog=changelog,
            **{k: v for k, v in kwargs.items() if k.startswith(_LND_IN_PREFIXES)},
        )
    if "datm_in" in adapt:
        adapt_datm_in(
            backend=backend, rundir=rundir, changelog=changelog,
            **{k: v for k, v in kwargs.items() if k.startswith(_DATM_IN_PREFIXES)},
        )
    if "mosart_in" in adapt:
        adapt_mosart_in(
            backend=backend, rundir=rundir, changelog=changelog,
            **{k: v for k, v in kwargs.items() if k.startswith(_MOSART_IN_PREFIXES)},
        )
    modelio_kwargs = {k: v for k, v in kwargs.items() if k.startswith(_MODELIO_PREFIXES)}
    for modelio_file in _MODELIO_FILES:
        if modelio_file in adapt:
            adapt_modelio(modelio_file, backend=backend, rundir=rundir, changelog=changelog, **modelio_kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Modify case namelists for eCLM-PDAF runs"
    )
    parser.add_argument(
        "-r", "--rundir",
        default=".",
        help="Directory containing the namelist files to modify (default: current directory)",
    )
    parser.add_argument(
        "-b", "--backend",
        choices=["f90nml", "re"],
        default="re",
        help="Backend for reading/writing namelists: 're' (default, regexp) or 'f90nml'",
    )
    parser.add_argument(
        "--no-changelog",
        action="store_true",
        default=False,
        help="Do not append the modification comment to the modified files",
    )
    parser.add_argument(
        "-a", "--adapt",
        nargs="+",
        default=["drv_in", "lnd_in", "datm_in", "mosart_in"],
        help=(
            "Which files to adapt. Values can be space- or comma-separated. "
            "Default: drv_flds_in drv_in lnd_in datm_in mosart_in. "
            "Modelio files (not in default): " + " ".join(_MODELIO_FILES)
        ),
    )

    # -------------------------------------------------------------------------
    # drv_flds_in groups
    # -------------------------------------------------------------------------
    group_megan = parser.add_argument_group("megan", "drv_flds_in &megan_emis_nl")
    group_megan.add_argument("--megan-megan_factors_file", type=str, default=None, help="megan_factors_file")
    group_megan.add_argument("--megan-megan_specifier", type=str, default=None, help="megan_specifier (full Fortran list string)")

    # -------------------------------------------------------------------------
    # drv_in groups
    # -------------------------------------------------------------------------
    group_timemgr = parser.add_argument_group("timemgr", "drv_in &seq_timemgr_inparm")
    group_timemgr.add_argument("--timemgr-start_ymd", type=str, default=None, help="start_ymd")
    group_timemgr.add_argument("--timemgr-start_tod", type=str, default=None, help="start_tod (seconds)")
    group_timemgr.add_argument("--timemgr-stop_ymd", type=str, default=None, help="stop_ymd")
    group_timemgr.add_argument("--timemgr-stop_tod", type=str, default=None, help="stop_tod (seconds)")
    group_timemgr.add_argument("--timemgr-stop_n", type=str, default=None, help="stop_n")
    group_timemgr.add_argument("--timemgr-stop_option", type=str, default=None, help="stop_option")
    group_timemgr.add_argument("--timemgr-restart_n", type=str, default=None, help="restart_n")
    group_timemgr.add_argument("--timemgr-restart_option", type=str, default=None, help="restart_option")
    group_timemgr.add_argument("--timemgr-restart_ymd", type=str, default=None, help="restart_ymd")
    group_timemgr.add_argument("--timemgr-calendar", type=str, default=None, help="calendar")
    group_timemgr.add_argument("--timemgr-atm_cpl_dt", type=str, default=None, help="atm coupling dt (s)")
    group_timemgr.add_argument("--timemgr-atm_cpl_offset", type=str, default=None, help="atm coupling offset")
    group_timemgr.add_argument("--timemgr-lnd_cpl_dt", type=str, default=None, help="lnd coupling dt (s)")
    group_timemgr.add_argument("--timemgr-lnd_cpl_offset", type=str, default=None, help="lnd coupling offset")
    group_timemgr.add_argument("--timemgr-ice_cpl_dt", type=str, default=None, help="ice coupling dt (s)")
    group_timemgr.add_argument("--timemgr-ice_cpl_offset", type=str, default=None, help="ice coupling offset")
    group_timemgr.add_argument("--timemgr-ocn_cpl_dt", type=str, default=None, help="ocn coupling dt (s)")
    group_timemgr.add_argument("--timemgr-ocn_cpl_offset", type=str, default=None, help="ocn coupling offset")
    group_timemgr.add_argument("--timemgr-rof_cpl_dt", type=str, default=None, help="rof coupling dt (s)")
    group_timemgr.add_argument("--timemgr-glc_cpl_dt", type=str, default=None, help="glc coupling dt (s)")
    group_timemgr.add_argument("--timemgr-glc_cpl_offset", type=str, default=None, help="glc coupling offset")
    group_timemgr.add_argument("--timemgr-wav_cpl_dt", type=str, default=None, help="wav coupling dt (s)")
    group_timemgr.add_argument("--timemgr-wav_cpl_offset", type=str, default=None, help="wav coupling offset")
    group_timemgr.add_argument("--timemgr-glc_avg_period", type=str, default=None, help="glc_avg_period")
    group_timemgr.add_argument("--timemgr-esp_cpl_offset", type=str, default=None, help="esp_cpl_offset")
    group_timemgr.add_argument("--timemgr-esp_run_on_pause", default=None, action=argparse.BooleanOptionalAction, help="esp_run_on_pause")
    group_timemgr.add_argument("--timemgr-end_restart", default=None, action=argparse.BooleanOptionalAction, help="end_restart")
    group_timemgr.add_argument("--timemgr-barrier_n", type=str, default=None, help="barrier_n")
    group_timemgr.add_argument("--timemgr-barrier_option", type=str, default=None, help="barrier_option")
    group_timemgr.add_argument("--timemgr-barrier_ymd", type=str, default=None, help="barrier_ymd")
    group_timemgr.add_argument("--timemgr-history_n", type=str, default=None, help="history_n")
    group_timemgr.add_argument("--timemgr-history_option", type=str, default=None, help="history_option")
    group_timemgr.add_argument("--timemgr-history_ymd", type=str, default=None, help="history_ymd")
    group_timemgr.add_argument("--timemgr-histavg_n", type=str, default=None, help="histavg_n")
    group_timemgr.add_argument("--timemgr-histavg_option", type=str, default=None, help="histavg_option")
    group_timemgr.add_argument("--timemgr-histavg_ymd", type=str, default=None, help="histavg_ymd")
    group_timemgr.add_argument("--timemgr-tprof_n", type=str, default=None, help="tprof_n")
    group_timemgr.add_argument("--timemgr-tprof_option", type=str, default=None, help="tprof_option")
    group_timemgr.add_argument("--timemgr-tprof_ymd", type=str, default=None, help="tprof_ymd")
    group_timemgr.add_argument("--timemgr-pause_n", type=str, default=None, help="pause_n")
    group_timemgr.add_argument("--timemgr-pause_option", type=str, default=None, help="pause_option")
    group_timemgr.add_argument("--timemgr-pause_active_atm", default=None, action=argparse.BooleanOptionalAction, help="pause_active_atm")
    group_timemgr.add_argument("--timemgr-pause_active_cpl", default=None, action=argparse.BooleanOptionalAction, help="pause_active_cpl")
    group_timemgr.add_argument("--timemgr-pause_active_glc", default=None, action=argparse.BooleanOptionalAction, help="pause_active_glc")
    group_timemgr.add_argument("--timemgr-pause_active_ice", default=None, action=argparse.BooleanOptionalAction, help="pause_active_ice")
    group_timemgr.add_argument("--timemgr-pause_active_lnd", default=None, action=argparse.BooleanOptionalAction, help="pause_active_lnd")
    group_timemgr.add_argument("--timemgr-pause_active_ocn", default=None, action=argparse.BooleanOptionalAction, help="pause_active_ocn")
    group_timemgr.add_argument("--timemgr-pause_active_rof", default=None, action=argparse.BooleanOptionalAction, help="pause_active_rof")
    group_timemgr.add_argument("--timemgr-pause_active_wav", default=None, action=argparse.BooleanOptionalAction, help="pause_active_wav")
    group_timemgr.add_argument("--timemgr-data_assimilation_atm", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_atm")
    group_timemgr.add_argument("--timemgr-data_assimilation_cpl", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_cpl")
    group_timemgr.add_argument("--timemgr-data_assimilation_glc", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_glc")
    group_timemgr.add_argument("--timemgr-data_assimilation_ice", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_ice")
    group_timemgr.add_argument("--timemgr-data_assimilation_lnd", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_lnd")
    group_timemgr.add_argument("--timemgr-data_assimilation_ocn", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_ocn")
    group_timemgr.add_argument("--timemgr-data_assimilation_rof", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_rof")
    group_timemgr.add_argument("--timemgr-data_assimilation_wav", default=None, action=argparse.BooleanOptionalAction, help="data_assimilation_wav")

    group_infodata = parser.add_argument_group("infodata", "drv_in &seq_infodata_inparm")
    group_infodata.add_argument("--infodata-username", type=str, default=None, help="username (default: $USER)")
    group_infodata.add_argument("--infodata-hostname", type=str, default=None, help="hostname (default: $SYSTEMNAME or $CPUNAME)")
    group_infodata.add_argument("--infodata-case_name", type=str, default=None, help="case_name")
    group_infodata.add_argument("--infodata-case_desc", type=str, default=None, help="case_desc")
    group_infodata.add_argument("--infodata-start_type", type=str, default=None, help="start_type (startup/continue/branch)")
    group_infodata.add_argument("--infodata-info_debug", type=str, default=None, help="info_debug verbosity level")
    group_infodata.add_argument("--infodata-outpathroot", type=str, default=None, help="outpathroot")
    group_infodata.add_argument("--infodata-restart_file", type=str, default=None, help="restart_file")
    group_infodata.add_argument("--infodata-force_stop_at", type=str, default=None, help="force_stop_at")
    group_infodata.add_argument("--infodata-wall_time_limit", type=str, default=None, help="wall_time_limit (hours, -1: unlimited)")
    group_infodata.add_argument("--infodata-do_budgets", default=None, action=argparse.BooleanOptionalAction, help="do_budgets")
    group_infodata.add_argument("--infodata-budget_ann", type=str, default=None, help="budget_ann")
    group_infodata.add_argument("--infodata-budget_daily", type=str, default=None, help="budget_daily")
    group_infodata.add_argument("--infodata-budget_inst", type=str, default=None, help="budget_inst")
    group_infodata.add_argument("--infodata-budget_ltann", type=str, default=None, help="budget_ltann")
    group_infodata.add_argument("--infodata-budget_ltend", type=str, default=None, help="budget_ltend")
    group_infodata.add_argument("--infodata-budget_month", type=str, default=None, help="budget_month")
    group_infodata.add_argument("--infodata-orb_mode", type=str, default=None, help="orb_mode")
    group_infodata.add_argument("--infodata-orb_iyear", type=str, default=None, help="orb_iyear")
    group_infodata.add_argument("--infodata-orb_iyear_align", type=str, default=None, help="orb_iyear_align")
    group_infodata.add_argument("--infodata-orb_eccen", type=str, default=None, help="orb_eccen")
    group_infodata.add_argument("--infodata-orb_obliq", type=str, default=None, help="orb_obliq")
    group_infodata.add_argument("--infodata-orb_mvelp", type=str, default=None, help="orb_mvelp")
    group_infodata.add_argument("--infodata-tfreeze_option", type=str, default=None, help="tfreeze_option")
    group_infodata.add_argument("--infodata-max_cplstep_time", type=str, default=None, help="max_cplstep_time")
    group_infodata.add_argument("--infodata-logfilepostfix", type=str, default=None, help="logfilepostfix")
    group_infodata.add_argument("--infodata-timing_dir", type=str, default=None, help="timing_dir")
    group_infodata.add_argument("--infodata-tchkpt_dir", type=str, default=None, help="tchkpt_dir")
    group_infodata.add_argument("--infodata-model_version", type=str, default=None, help="model_version")

    group_driver = parser.add_argument_group("driver", "drv_in &cime_driver_inst")
    group_driver.add_argument("--driver-ninst_driver", type=str, default=None, help="ninst_driver")

    group_pes = parser.add_argument_group("pes", "drv_in &cime_pes")
    for _comp in ("atm", "esp", "glc", "ice", "lnd", "ocn", "rof", "wav"):
        group_pes.add_argument(f"--pes-{_comp}_layout", type=str, default=None, help=f"{_comp}_layout")
        group_pes.add_argument(f"--pes-{_comp}_ntasks", type=str, default=None, help=f"{_comp}_ntasks")
        group_pes.add_argument(f"--pes-{_comp}_nthreads", type=str, default=None, help=f"{_comp}_nthreads")
        group_pes.add_argument(f"--pes-{_comp}_pestride", type=str, default=None, help=f"{_comp}_pestride")
        group_pes.add_argument(f"--pes-{_comp}_rootpe", type=str, default=None, help=f"{_comp}_rootpe")
    for _comp in ("cpl",):
        group_pes.add_argument(f"--pes-{_comp}_ntasks", type=str, default=None, help=f"{_comp}_ntasks")
        group_pes.add_argument(f"--pes-{_comp}_nthreads", type=str, default=None, help=f"{_comp}_nthreads")
        group_pes.add_argument(f"--pes-{_comp}_pestride", type=str, default=None, help=f"{_comp}_pestride")
        group_pes.add_argument(f"--pes-{_comp}_rootpe", type=str, default=None, help=f"{_comp}_rootpe")

    group_esmf = parser.add_argument_group("esmf", "drv_in &esmf_inparm")
    group_esmf.add_argument("--esmf-esmf_logfile_kind", type=str, default=None, help="esmf_logfile_kind")

    group_papi = parser.add_argument_group("papi", "drv_in &papi_inparm")
    group_papi.add_argument("--papi-papi_ctr1_str", type=str, default=None, help="papi_ctr1_str")
    group_papi.add_argument("--papi-papi_ctr2_str", type=str, default=None, help="papi_ctr2_str")
    group_papi.add_argument("--papi-papi_ctr3_str", type=str, default=None, help="papi_ctr3_str")
    group_papi.add_argument("--papi-papi_ctr4_str", type=str, default=None, help="papi_ctr4_str")

    group_pio = parser.add_argument_group("pio", "drv_in &pio_default_inparm")
    group_pio.add_argument("--pio-pio_async_interface", default=None, action=argparse.BooleanOptionalAction, help="pio_async_interface")
    group_pio.add_argument("--pio-pio_blocksize", type=str, default=None, help="pio_blocksize")
    group_pio.add_argument("--pio-pio_buffer_size_limit", type=str, default=None, help="pio_buffer_size_limit")
    group_pio.add_argument("--pio-pio_debug_level", type=str, default=None, help="pio_debug_level")
    group_pio.add_argument("--pio-pio_rearr_comm_enable_hs_comp2io", default=None, action=argparse.BooleanOptionalAction, help="pio_rearr_comm_enable_hs_comp2io")
    group_pio.add_argument("--pio-pio_rearr_comm_enable_hs_io2comp", default=None, action=argparse.BooleanOptionalAction, help="pio_rearr_comm_enable_hs_io2comp")
    group_pio.add_argument("--pio-pio_rearr_comm_enable_isend_comp2io", default=None, action=argparse.BooleanOptionalAction, help="pio_rearr_comm_enable_isend_comp2io")
    group_pio.add_argument("--pio-pio_rearr_comm_enable_isend_io2comp", default=None, action=argparse.BooleanOptionalAction, help="pio_rearr_comm_enable_isend_io2comp")
    group_pio.add_argument("--pio-pio_rearr_comm_fcd", type=str, default=None, help="pio_rearr_comm_fcd")
    group_pio.add_argument("--pio-pio_rearr_comm_max_pend_req_comp2io", type=str, default=None, help="pio_rearr_comm_max_pend_req_comp2io")
    group_pio.add_argument("--pio-pio_rearr_comm_max_pend_req_io2comp", type=str, default=None, help="pio_rearr_comm_max_pend_req_io2comp")
    group_pio.add_argument("--pio-pio_rearr_comm_type", type=str, default=None, help="pio_rearr_comm_type")

    group_prof = parser.add_argument_group("prof", "drv_in &prof_inparm")
    group_prof.add_argument("--prof-profile_add_detail", default=None, action=argparse.BooleanOptionalAction, help="profile_add_detail")
    group_prof.add_argument("--prof-profile_barrier", default=None, action=argparse.BooleanOptionalAction, help="profile_barrier")
    group_prof.add_argument("--prof-profile_depth_limit", type=str, default=None, help="profile_depth_limit")
    group_prof.add_argument("--prof-profile_detail_limit", type=str, default=None, help="profile_detail_limit")
    group_prof.add_argument("--prof-profile_disable", default=None, action=argparse.BooleanOptionalAction, help="profile_disable")
    group_prof.add_argument("--prof-profile_global_stats", default=None, action=argparse.BooleanOptionalAction, help="profile_global_stats")
    group_prof.add_argument("--prof-profile_outpe_num", type=str, default=None, help="profile_outpe_num")
    group_prof.add_argument("--prof-profile_outpe_stride", type=str, default=None, help="profile_outpe_stride")
    group_prof.add_argument("--prof-profile_ovhd_measurement", default=None, action=argparse.BooleanOptionalAction, help="profile_ovhd_measurement")
    group_prof.add_argument("--prof-profile_papi_enable", default=None, action=argparse.BooleanOptionalAction, help="profile_papi_enable")
    group_prof.add_argument("--prof-profile_single_file", default=None, action=argparse.BooleanOptionalAction, help="profile_single_file")
    group_prof.add_argument("--prof-profile_timer", type=str, default=None, help="profile_timer")

    group_cplflds = parser.add_argument_group("cplflds", "drv_in &seq_cplflds_inparm")
    group_cplflds.add_argument("--cplflds-flds_bgc_oi", default=None, action=argparse.BooleanOptionalAction, help="flds_bgc_oi")
    group_cplflds.add_argument("--cplflds-flds_co2_dmsa", default=None, action=argparse.BooleanOptionalAction, help="flds_co2_dmsa")
    group_cplflds.add_argument("--cplflds-flds_co2a", default=None, action=argparse.BooleanOptionalAction, help="flds_co2a")
    group_cplflds.add_argument("--cplflds-flds_co2b", default=None, action=argparse.BooleanOptionalAction, help="flds_co2b")
    group_cplflds.add_argument("--cplflds-flds_co2c", default=None, action=argparse.BooleanOptionalAction, help="flds_co2c")
    group_cplflds.add_argument("--cplflds-flds_wiso", default=None, action=argparse.BooleanOptionalAction, help="flds_wiso")
    group_cplflds.add_argument("--cplflds-glc_nec", type=str, default=None, help="glc_nec")
    group_cplflds.add_argument("--cplflds-ice_ncat", type=str, default=None, help="ice_ncat")
    group_cplflds.add_argument("--cplflds-nan_check_component_fields", default=None, action=argparse.BooleanOptionalAction, help="nan_check_component_fields")
    group_cplflds.add_argument("--cplflds-seq_flds_i2o_per_cat", default=None, action=argparse.BooleanOptionalAction, help="seq_flds_i2o_per_cat")

    group_cplcustom = parser.add_argument_group("cplcustom", "drv_in &seq_cplflds_userspec")
    group_cplcustom.add_argument("--cplcustom-cplflds_custom", type=str, default=None, help="cplflds_custom")

    group_flux_mct = parser.add_argument_group("flux_mct", "drv_in &seq_flux_mct_inparm")
    group_flux_mct.add_argument("--flux_mct-seq_flux_atmocn_minwind", type=str, default=None, help="seq_flux_atmocn_minwind")
    group_flux_mct.add_argument("--flux_mct-seq_flux_mct_albdif", type=str, default=None, help="seq_flux_mct_albdif")
    group_flux_mct.add_argument("--flux_mct-seq_flux_mct_albdir", type=str, default=None, help="seq_flux_mct_albdir")

    # -------------------------------------------------------------------------
    # lnd_in groups
    # -------------------------------------------------------------------------
    group_clm_inparm = parser.add_argument_group("clm_inparm", "lnd_in &clm_inparm")
    group_clm_inparm.add_argument("--clm_inparm-finidat", type=str, default=None, help="finidat (initial conditions file)")
    group_clm_inparm.add_argument("--clm_inparm-fsurdat", type=str, default=None, help="fsurdat (surface data file)")
    group_clm_inparm.add_argument("--clm_inparm-fatmlndfrc", type=str, default=None, help="fatmlndfrc (domain file)")
    group_clm_inparm.add_argument("--clm_inparm-paramfile", type=str, default=None, help="paramfile (CLM parameter file)")
    group_clm_inparm.add_argument("--clm_inparm-fsnowaging", type=str, default=None, help="fsnowaging")
    group_clm_inparm.add_argument("--clm_inparm-fsnowoptics", type=str, default=None, help="fsnowoptics")
    group_clm_inparm.add_argument("--clm_inparm-dtime", type=str, default=None, help="dtime (CLM time step, s)")
    group_clm_inparm.add_argument("--clm_inparm-co2_ppmv", type=str, default=None, help="co2_ppmv")
    group_clm_inparm.add_argument("--clm_inparm-co2_type", type=str, default=None, help="co2_type")
    group_clm_inparm.add_argument("--clm_inparm-spinup_state", type=str, default=None, help="spinup_state (0: normal, 1: AD, 2: post-AD)")
    group_clm_inparm.add_argument("--clm_inparm-hist_mfilt", type=str, default=None, help="hist_mfilt (history file max frames)")
    group_clm_inparm.add_argument("--clm_inparm-hist_nhtfrq", type=str, default=None, help="hist_nhtfrq (history write frequency)")
    group_clm_inparm.add_argument("--clm_inparm-hist_fincl1", type=str, default=None, help="hist_fincl1 (history fields, full Fortran list string)")
    group_clm_inparm.add_argument("--clm_inparm-hist_empty_htapes", default=None, action=argparse.BooleanOptionalAction, help="hist_empty_htapes")
    group_clm_inparm.add_argument("--clm_inparm-irrigate", default=None, action=argparse.BooleanOptionalAction, help="irrigate")
    group_clm_inparm.add_argument("--clm_inparm-albice", type=str, default=None, help="albice (visible,NIR fractions)")
    group_clm_inparm.add_argument("--clm_inparm-h2osno_max", type=str, default=None, help="h2osno_max")
    group_clm_inparm.add_argument("--clm_inparm-int_snow_max", type=str, default=None, help="int_snow_max")
    group_clm_inparm.add_argument("--clm_inparm-nlevsno", type=str, default=None, help="nlevsno (snow layers)")
    group_clm_inparm.add_argument("--clm_inparm-nsegspc", type=str, default=None, help="nsegspc")
    group_clm_inparm.add_argument("--clm_inparm-maxpatch_glcmec", type=str, default=None, help="maxpatch_glcmec")
    group_clm_inparm.add_argument("--clm_inparm-maxpatch_pft", type=str, default=None, help="maxpatch_pft")
    group_clm_inparm.add_argument("--clm_inparm-n_melt_glcmec", type=str, default=None, help="n_melt_glcmec")
    group_clm_inparm.add_argument("--clm_inparm-glc_do_dynglacier", default=None, action=argparse.BooleanOptionalAction, help="glc_do_dynglacier")
    group_clm_inparm.add_argument("--clm_inparm-glc_snow_persistence_max_days", type=str, default=None, help="glc_snow_persistence_max_days")
    group_clm_inparm.add_argument("--clm_inparm-soil_layerstruct", type=str, default=None, help="soil_layerstruct")
    group_clm_inparm.add_argument("--clm_inparm-suplnitro", type=str, default=None, help="suplnitro")
    group_clm_inparm.add_argument("--clm_inparm-run_zero_weight_urban", default=None, action=argparse.BooleanOptionalAction, help="run_zero_weight_urban")
    group_clm_inparm.add_argument("--clm_inparm-snow_thermal_cond_method", type=str, default=None, help="snow_thermal_cond_method")
    group_clm_inparm.add_argument("--clm_inparm-snow_thermal_cond_glc_method", type=str, default=None, help="snow_thermal_cond_glc_method")
    group_clm_inparm.add_argument("--clm_inparm-snow_thermal_cond_lake_method", type=str, default=None, help="snow_thermal_cond_lake_method")
    group_clm_inparm.add_argument("--clm_inparm-create_crop_landunit", default=None, action=argparse.BooleanOptionalAction, help="create_crop_landunit")
    group_clm_inparm.add_argument("--clm_inparm-use_cn", default=None, action=argparse.BooleanOptionalAction, help="use_cn")
    group_clm_inparm.add_argument("--clm_inparm-use_crop", default=None, action=argparse.BooleanOptionalAction, help="use_crop")
    group_clm_inparm.add_argument("--clm_inparm-use_fertilizer", default=None, action=argparse.BooleanOptionalAction, help="use_fertilizer")
    group_clm_inparm.add_argument("--clm_inparm-use_flexiblecn", default=None, action=argparse.BooleanOptionalAction, help="use_flexiblecn")
    group_clm_inparm.add_argument("--clm_inparm-use_fun", default=None, action=argparse.BooleanOptionalAction, help="use_fun")
    group_clm_inparm.add_argument("--clm_inparm-use_grainproduct", default=None, action=argparse.BooleanOptionalAction, help="use_grainproduct")
    group_clm_inparm.add_argument("--clm_inparm-use_hydrstress", default=None, action=argparse.BooleanOptionalAction, help="use_hydrstress")
    group_clm_inparm.add_argument("--clm_inparm-use_lai_streams", default=None, action=argparse.BooleanOptionalAction, help="use_lai_streams")
    group_clm_inparm.add_argument("--clm_inparm-use_lch4", default=None, action=argparse.BooleanOptionalAction, help="use_lch4")
    group_clm_inparm.add_argument("--clm_inparm-use_luna", default=None, action=argparse.BooleanOptionalAction, help="use_luna")
    group_clm_inparm.add_argument("--clm_inparm-use_nguardrail", default=None, action=argparse.BooleanOptionalAction, help="use_nguardrail")
    group_clm_inparm.add_argument("--clm_inparm-use_nitrif_denitrif", default=None, action=argparse.BooleanOptionalAction, help="use_nitrif_denitrif")
    group_clm_inparm.add_argument("--clm_inparm-use_soil_moisture_streams", default=None, action=argparse.BooleanOptionalAction, help="use_soil_moisture_streams")
    group_clm_inparm.add_argument("--clm_inparm-use_vertsoilc", default=None, action=argparse.BooleanOptionalAction, help="use_vertsoilc")
    group_clm_inparm.add_argument("--clm_inparm-use_bedrock", default=None, action=argparse.BooleanOptionalAction, help="use_bedrock")
    group_clm_inparm.add_argument("--clm_inparm-use_century_decomp", default=None, action=argparse.BooleanOptionalAction, help="use_century_decomp")
    group_clm_inparm.add_argument("--clm_inparm-use_dynroot", default=None, action=argparse.BooleanOptionalAction, help="use_dynroot")
    group_clm_inparm.add_argument("--clm_inparm-use_fates", default=None, action=argparse.BooleanOptionalAction, help="use_fates")

    group_ndepdyn = parser.add_argument_group("ndepdyn", "lnd_in &ndepdyn_nml")
    group_ndepdyn.add_argument("--ndepdyn-ndep_taxmode", type=str, default=None, help="ndep_taxmode")
    group_ndepdyn.add_argument("--ndepdyn-ndep_varlist", type=str, default=None, help="ndep_varlist")
    group_ndepdyn.add_argument("--ndepdyn-ndepmapalgo", type=str, default=None, help="ndepmapalgo")
    group_ndepdyn.add_argument("--ndepdyn-stream_fldfilename_ndep", type=str, default=None, help="stream_fldfilename_ndep")
    group_ndepdyn.add_argument("--ndepdyn-stream_year_first_ndep", type=str, default=None, help="stream_year_first_ndep")
    group_ndepdyn.add_argument("--ndepdyn-stream_year_last_ndep", type=str, default=None, help="stream_year_last_ndep")

    group_popd = parser.add_argument_group("popd", "lnd_in &popd_streams")
    group_popd.add_argument("--popd-popdensmapalgo", type=str, default=None, help="popdensmapalgo")
    group_popd.add_argument("--popd-stream_fldfilename_popdens", type=str, default=None, help="stream_fldfilename_popdens")
    group_popd.add_argument("--popd-stream_year_first_popdens", type=str, default=None, help="stream_year_first_popdens")
    group_popd.add_argument("--popd-stream_year_last_popdens", type=str, default=None, help="stream_year_last_popdens")

    group_urbantv = parser.add_argument_group("urbantv", "lnd_in &urbantv_streams")
    group_urbantv.add_argument("--urbantv-stream_fldfilename_urbantv", type=str, default=None, help="stream_fldfilename_urbantv")
    group_urbantv.add_argument("--urbantv-stream_year_first_urbantv", type=str, default=None, help="stream_year_first_urbantv")
    group_urbantv.add_argument("--urbantv-stream_year_last_urbantv", type=str, default=None, help="stream_year_last_urbantv")
    group_urbantv.add_argument("--urbantv-urbantvmapalgo", type=str, default=None, help="urbantvmapalgo")

    group_light = parser.add_argument_group("light", "lnd_in &light_streams")
    group_light.add_argument("--light-lightngmapalgo", type=str, default=None, help="lightngmapalgo")
    group_light.add_argument("--light-stream_fldfilename_lightng", type=str, default=None, help="stream_fldfilename_lightng")
    group_light.add_argument("--light-stream_year_first_lightng", type=str, default=None, help="stream_year_first_lightng")
    group_light.add_argument("--light-stream_year_last_lightng", type=str, default=None, help="stream_year_last_lightng")

    group_atm2lnd = parser.add_argument_group("atm2lnd", "lnd_in &atm2lnd_inparm")
    group_atm2lnd.add_argument("--atm2lnd-glcmec_downscale_longwave", default=None, action=argparse.BooleanOptionalAction, help="glcmec_downscale_longwave")
    group_atm2lnd.add_argument("--atm2lnd-lapse_rate", type=str, default=None, help="lapse_rate")
    group_atm2lnd.add_argument("--atm2lnd-lapse_rate_longwave", type=str, default=None, help="lapse_rate_longwave")
    group_atm2lnd.add_argument("--atm2lnd-longwave_downscaling_limit", type=str, default=None, help="longwave_downscaling_limit")
    group_atm2lnd.add_argument("--atm2lnd-precip_repartition_glc_all_rain_t", type=str, default=None, help="precip_repartition_glc_all_rain_t")
    group_atm2lnd.add_argument("--atm2lnd-precip_repartition_glc_all_snow_t", type=str, default=None, help="precip_repartition_glc_all_snow_t")
    group_atm2lnd.add_argument("--atm2lnd-precip_repartition_nonglc_all_rain_t", type=str, default=None, help="precip_repartition_nonglc_all_rain_t")
    group_atm2lnd.add_argument("--atm2lnd-precip_repartition_nonglc_all_snow_t", type=str, default=None, help="precip_repartition_nonglc_all_snow_t")
    group_atm2lnd.add_argument("--atm2lnd-repartition_rain_snow", default=None, action=argparse.BooleanOptionalAction, help="repartition_rain_snow")

    group_lnd2atm = parser.add_argument_group("lnd2atm", "lnd_in &lnd2atm_inparm")
    group_lnd2atm.add_argument("--lnd2atm-melt_non_icesheet_ice_runoff", default=None, action=argparse.BooleanOptionalAction, help="melt_non_icesheet_ice_runoff")

    group_canopyhydro = parser.add_argument_group("canopyhydro", "lnd_in &clm_canopyhydrology_inparm")
    group_canopyhydro.add_argument("--canopyhydro-interception_fraction", type=str, default=None, help="interception_fraction")
    group_canopyhydro.add_argument("--canopyhydro-maximum_leaf_wetted_fraction", type=str, default=None, help="maximum_leaf_wetted_fraction")
    group_canopyhydro.add_argument("--canopyhydro-snowveg_flag", type=str, default=None, help="snowveg_flag")
    group_canopyhydro.add_argument("--canopyhydro-use_clm5_fpi", default=None, action=argparse.BooleanOptionalAction, help="use_clm5_fpi")

    group_cnphenology = parser.add_argument_group("cnphenology", "lnd_in &cnphenology")
    group_cnphenology.add_argument("--cnphenology-initial_seed_at_planting", type=str, default=None, help="initial_seed_at_planting")

    group_cnvegcarbon = parser.add_argument_group("cnvegcarbon", "lnd_in &cnvegcarbonstate")
    group_cnvegcarbon.add_argument("--cnvegcarbon-initial_vegc", type=str, default=None, help="initial_vegc")

    group_century = parser.add_argument_group("century", "lnd_in &century_soilbgcdecompcascade")
    group_century.add_argument("--century-initial_cstocks", type=str, default=None, help="initial_cstocks (Fortran list, e.g. '200.0d00, 200.0d00, 200.0d00')")
    group_century.add_argument("--century-initial_cstocks_depth", type=str, default=None, help="initial_cstocks_depth")

    group_soilhydro = parser.add_argument_group("soilhydro", "lnd_in &soilhydrology_inparm")
    group_soilhydro.add_argument("--soilhydro-baseflow_scalar", type=str, default=None, help="baseflow_scalar")

    group_luna = parser.add_argument_group("luna", "lnd_in &luna")
    group_luna.add_argument("--luna-jmaxb1", type=str, default=None, help="jmaxb1")

    group_friction = parser.add_argument_group("friction", "lnd_in &friction_velocity")
    group_friction.add_argument("--friction-zetamaxstable", type=str, default=None, help="zetamaxstable")

    group_soilwater = parser.add_argument_group("soilwater", "lnd_in &soilwater_movement_inparm")
    group_soilwater.add_argument("--soilwater-dtmin", type=str, default=None, help="dtmin")
    group_soilwater.add_argument("--soilwater-expensive", type=str, default=None, help="expensive")
    group_soilwater.add_argument("--soilwater-flux_calculation", type=str, default=None, help="flux_calculation")
    group_soilwater.add_argument("--soilwater-inexpensive", type=str, default=None, help="inexpensive")
    group_soilwater.add_argument("--soilwater-lower_boundary_condition", type=str, default=None, help="lower_boundary_condition")
    group_soilwater.add_argument("--soilwater-soilwater_movement_method", type=str, default=None, help="soilwater_movement_method")
    group_soilwater.add_argument("--soilwater-upper_boundary_condition", type=str, default=None, help="upper_boundary_condition")
    group_soilwater.add_argument("--soilwater-verysmall", type=str, default=None, help="verysmall")
    group_soilwater.add_argument("--soilwater-xtolerlower", type=str, default=None, help="xtolerlower")
    group_soilwater.add_argument("--soilwater-xtolerupper", type=str, default=None, help="xtolerupper")

    group_rooting = parser.add_argument_group("rooting", "lnd_in &rooting_profile_inparm")
    group_rooting.add_argument("--rooting-rooting_profile_method_carbon", type=str, default=None, help="rooting_profile_method_carbon")
    group_rooting.add_argument("--rooting-rooting_profile_method_water", type=str, default=None, help="rooting_profile_method_water")

    group_soil_resis = parser.add_argument_group("soil_resis", "lnd_in &soil_resis_inparm")
    group_soil_resis.add_argument("--soil_resis-soil_resis_method", type=str, default=None, help="soil_resis_method")

    group_bgc_shared = parser.add_argument_group("bgc_shared", "lnd_in &bgc_shared")
    group_bgc_shared.add_argument("--bgc_shared-constrain_stress_deciduous_onset", default=None, action=argparse.BooleanOptionalAction, help="constrain_stress_deciduous_onset")
    group_bgc_shared.add_argument("--bgc_shared-decomp_depth_efolding", type=str, default=None, help="decomp_depth_efolding")

    group_canopyflux = parser.add_argument_group("canopyflux", "lnd_in &canopyfluxes_inparm")
    group_canopyflux.add_argument("--canopyflux-use_undercanopy_stability", default=None, action=argparse.BooleanOptionalAction, help="use_undercanopy_stability")

    group_aerosol = parser.add_argument_group("aerosol", "lnd_in &aerosol")
    group_aerosol.add_argument("--aerosol-fresh_snw_rds_max", type=str, default=None, help="fresh_snw_rds_max")

    group_clmu = parser.add_argument_group("clmu", "lnd_in &clmu_inparm")
    group_clmu.add_argument("--clmu-building_temp_method", type=str, default=None, help="building_temp_method")
    group_clmu.add_argument("--clmu-urban_hac", type=str, default=None, help="urban_hac")
    group_clmu.add_argument("--clmu-urban_traffic", default=None, action=argparse.BooleanOptionalAction, help="urban_traffic")

    group_clm_soilstate = parser.add_argument_group("clm_soilstate", "lnd_in &clm_soilstate_inparm")
    group_clm_soilstate.add_argument("--clm_soilstate-organic_frac_squared", default=None, action=argparse.BooleanOptionalAction, help="organic_frac_squared")

    group_clm_nitrogen = parser.add_argument_group("clm_nitrogen", "lnd_in &clm_nitrogen")
    group_clm_nitrogen.add_argument("--clm_nitrogen-carbon_resp_opt", type=str, default=None, help="carbon_resp_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-cn_evergreen_phenology_opt", type=str, default=None, help="cn_evergreen_phenology_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-cn_partition_opt", type=str, default=None, help="cn_partition_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-cn_residual_opt", type=str, default=None, help="cn_residual_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-cnratio_floating", default=None, action=argparse.BooleanOptionalAction, help="cnratio_floating")
    group_clm_nitrogen.add_argument("--clm_nitrogen-downreg_opt", default=None, action=argparse.BooleanOptionalAction, help="downreg_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-lnc_opt", default=None, action=argparse.BooleanOptionalAction, help="lnc_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-mm_nuptake_opt", default=None, action=argparse.BooleanOptionalAction, help="mm_nuptake_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-nscalar_opt", default=None, action=argparse.BooleanOptionalAction, help="nscalar_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-plant_ndemand_opt", type=str, default=None, help="plant_ndemand_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-reduce_dayl_factor", default=None, action=argparse.BooleanOptionalAction, help="reduce_dayl_factor")
    group_clm_nitrogen.add_argument("--clm_nitrogen-substrate_term_opt", default=None, action=argparse.BooleanOptionalAction, help="substrate_term_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-temp_scalar_opt", default=None, action=argparse.BooleanOptionalAction, help="temp_scalar_opt")
    group_clm_nitrogen.add_argument("--clm_nitrogen-vcmax_opt", type=str, default=None, help="vcmax_opt")

    group_clm_snowhydro = parser.add_argument_group("clm_snowhydro", "lnd_in &clm_snowhydrology_inparm")
    group_clm_snowhydro.add_argument("--clm_snowhydro-lotmp_snowdensity_method", type=str, default=None, help="lotmp_snowdensity_method")
    group_clm_snowhydro.add_argument("--clm_snowhydro-reset_snow", default=None, action=argparse.BooleanOptionalAction, help="reset_snow")
    group_clm_snowhydro.add_argument("--clm_snowhydro-reset_snow_glc", default=None, action=argparse.BooleanOptionalAction, help="reset_snow_glc")
    group_clm_snowhydro.add_argument("--clm_snowhydro-reset_snow_glc_ela", type=str, default=None, help="reset_snow_glc_ela")
    group_clm_snowhydro.add_argument("--clm_snowhydro-snow_overburden_compaction_method", type=str, default=None, help="snow_overburden_compaction_method")
    group_clm_snowhydro.add_argument("--clm_snowhydro-upplim_destruct_metamorph", type=str, default=None, help="upplim_destruct_metamorph")
    group_clm_snowhydro.add_argument("--clm_snowhydro-wind_dependent_snow_density", default=None, action=argparse.BooleanOptionalAction, help="wind_dependent_snow_density")

    group_cnprecision = parser.add_argument_group("cnprecision", "lnd_in &cnprecision_inparm")
    group_cnprecision.add_argument("--cnprecision-cnegcrit", type=str, default=None, help="cnegcrit")
    group_cnprecision.add_argument("--cnprecision-ncrit", type=str, default=None, help="ncrit")
    group_cnprecision.add_argument("--cnprecision-nnegcrit", type=str, default=None, help="nnegcrit")

    group_glacier = parser.add_argument_group("glacier", "lnd_in &clm_glacier_behavior")
    group_glacier.add_argument("--glacier-glacier_region_behavior", type=str, default=None, help="glacier_region_behavior (full Fortran list string)")
    group_glacier.add_argument("--glacier-glacier_region_ice_runoff_behavior", type=str, default=None, help="glacier_region_ice_runoff_behavior (full Fortran list string)")
    group_glacier.add_argument("--glacier-glacier_region_melt_behavior", type=str, default=None, help="glacier_region_melt_behavior (full Fortran list string)")
    group_glacier.add_argument("--glacier-glacier_region_rain_to_snow_behavior", type=str, default=None, help="glacier_region_rain_to_snow_behavior (full Fortran list string)")

    group_crop = parser.add_argument_group("crop", "lnd_in &crop")
    group_crop.add_argument("--crop-baset_latvary_intercept", type=str, default=None, help="baset_latvary_intercept")
    group_crop.add_argument("--crop-baset_latvary_slope", type=str, default=None, help="baset_latvary_slope")
    group_crop.add_argument("--crop-baset_mapping", type=str, default=None, help="baset_mapping")

    group_irrigation = parser.add_argument_group("irrigation", "lnd_in &irrigation_inparm")
    group_irrigation.add_argument("--irrigation-irrig_depth", type=str, default=None, help="irrig_depth")
    group_irrigation.add_argument("--irrigation-irrig_length", type=str, default=None, help="irrig_length")
    group_irrigation.add_argument("--irrigation-irrig_min_lai", type=str, default=None, help="irrig_min_lai")
    group_irrigation.add_argument("--irrigation-irrig_start_time", type=str, default=None, help="irrig_start_time")
    group_irrigation.add_argument("--irrigation-irrig_target_smp", type=str, default=None, help="irrig_target_smp")
    group_irrigation.add_argument("--irrigation-irrig_threshold_fraction", type=str, default=None, help="irrig_threshold_fraction")
    group_irrigation.add_argument("--irrigation-limit_irrigation_if_rof_enabled", default=None, action=argparse.BooleanOptionalAction, help="limit_irrigation_if_rof_enabled")

    group_ch4 = parser.add_argument_group("ch4", "lnd_in &ch4par_in")
    group_ch4.add_argument("--ch4-finundation_method", type=str, default=None, help="finundation_method")
    group_ch4.add_argument("--ch4-use_aereoxid_prog", default=None, action=argparse.BooleanOptionalAction, help="use_aereoxid_prog")

    group_humanindex = parser.add_argument_group("humanindex", "lnd_in &clm_humanindex_inparm")
    group_humanindex.add_argument("--humanindex-calc_human_stress_indices", type=str, default=None, help="calc_human_stress_indices")

    group_cnmresp = parser.add_argument_group("cnmresp", "lnd_in &cnmresp_inparm")
    group_cnmresp.add_argument("--cnmresp-br_root", type=str, default=None, help="br_root")

    group_photosyns = parser.add_argument_group("photosyns", "lnd_in &photosyns_inparm")
    group_photosyns.add_argument("--photosyns-leafresp_method", type=str, default=None, help="leafresp_method")
    group_photosyns.add_argument("--photosyns-light_inhibit", default=None, action=argparse.BooleanOptionalAction, help="light_inhibit")
    group_photosyns.add_argument("--photosyns-modifyphoto_and_lmr_forcrop", default=None, action=argparse.BooleanOptionalAction, help="modifyphoto_and_lmr_forcrop")
    group_photosyns.add_argument("--photosyns-rootstem_acc", default=None, action=argparse.BooleanOptionalAction, help="rootstem_acc")
    group_photosyns.add_argument("--photosyns-stomatalcond_method", type=str, default=None, help="stomatalcond_method")

    group_cnfire = parser.add_argument_group("cnfire", "lnd_in &cnfire_inparm")
    group_cnfire.add_argument("--cnfire-fire_method", type=str, default=None, help="fire_method")

    group_cn_general = parser.add_argument_group("cn_general", "lnd_in &cn_general")
    group_cn_general.add_argument("--cn_general-dribble_crophrv_xsmrpool_2atm", default=None, action=argparse.BooleanOptionalAction, help="dribble_crophrv_xsmrpool_2atm")

    group_lifire = parser.add_argument_group("lifire", "lnd_in &lifire_inparm")
    group_lifire.add_argument("--lifire-boreal_peatfire_c", type=str, default=None, help="boreal_peatfire_c")
    group_lifire.add_argument("--lifire-bt_max", type=str, default=None, help="bt_max")
    group_lifire.add_argument("--lifire-bt_min", type=str, default=None, help="bt_min")
    group_lifire.add_argument("--lifire-cli_scale", type=str, default=None, help="cli_scale")
    group_lifire.add_argument("--lifire-cmb_cmplt_fact", type=str, default=None, help="cmb_cmplt_fact (Fortran list, e.g. '0.5d00, 0.28d00')")
    group_lifire.add_argument("--lifire-cropfire_a1", type=str, default=None, help="cropfire_a1")
    group_lifire.add_argument("--lifire-lfuel", type=str, default=None, help="lfuel")
    group_lifire.add_argument("--lifire-non_boreal_peatfire_c", type=str, default=None, help="non_boreal_peatfire_c")
    group_lifire.add_argument("--lifire-occur_hi_gdp_tree", type=str, default=None, help="occur_hi_gdp_tree")
    group_lifire.add_argument("--lifire-pot_hmn_ign_counts_alpha", type=str, default=None, help="pot_hmn_ign_counts_alpha")
    group_lifire.add_argument("--lifire-rh_hgh", type=str, default=None, help="rh_hgh")
    group_lifire.add_argument("--lifire-rh_low", type=str, default=None, help="rh_low")
    group_lifire.add_argument("--lifire-ufuel", type=str, default=None, help="ufuel")

    group_ch4finundated = parser.add_argument_group("ch4finundated", "lnd_in &ch4finundated")
    group_ch4finundated.add_argument("--ch4finundated-stream_fldfilename_ch4finundated", type=str, default=None, help="stream_fldfilename_ch4finundated")

    group_clm_canopy = parser.add_argument_group("clm_canopy", "lnd_in &clm_canopy_inparm")
    group_clm_canopy.add_argument("--clm_canopy-leaf_mr_vcm", type=str, default=None, help="leaf_mr_vcm")

    # -------------------------------------------------------------------------
    # datm_in groups
    # -------------------------------------------------------------------------
    group_datm_nml = parser.add_argument_group("datm_nml", "datm_in &datm_nml")
    group_datm_nml.add_argument("--datm_nml-decomp", type=str, default=None, help="decomp")
    group_datm_nml.add_argument("--datm_nml-factorfn", type=str, default=None, help="factorfn")
    group_datm_nml.add_argument("--datm_nml-force_prognostic_true", default=None, action=argparse.BooleanOptionalAction, help="force_prognostic_true")
    group_datm_nml.add_argument("--datm_nml-iradsw", type=str, default=None, help="iradsw")
    group_datm_nml.add_argument("--datm_nml-presaero", default=None, action=argparse.BooleanOptionalAction, help="presaero")
    group_datm_nml.add_argument("--datm_nml-restfilm", type=str, default=None, help="restfilm")
    group_datm_nml.add_argument("--datm_nml-restfils", type=str, default=None, help="restfils")
    group_datm_nml.add_argument("--datm_nml-wiso_datm", default=None, action=argparse.BooleanOptionalAction, help="wiso_datm")

    group_shr_strdata = parser.add_argument_group("shr_strdata_nml", "datm_in &shr_strdata_nml")
    group_shr_strdata.add_argument("--shr_strdata_nml-datamode", type=str, default=None, help="datamode")
    group_shr_strdata.add_argument("--shr_strdata_nml-domainfile", type=str, default=None, help="domainfile")
    group_shr_strdata.add_argument("--shr_strdata_nml-dtlimit", type=str, default=None, help="dtlimit (full Fortran list string)")
    group_shr_strdata.add_argument("--shr_strdata_nml-streams", type=str, default=None, help="streams (full Fortran list string)")
    group_shr_strdata.add_argument("--shr_strdata_nml-vectors", type=str, default=None, help="vectors")

    # -------------------------------------------------------------------------
    # mosart_in groups
    # -------------------------------------------------------------------------
    group_mosart = parser.add_argument_group("mosart_inparm", "mosart_in &mosart_inparm")
    group_mosart.add_argument("--mosart_inparm-bypass_routing_option", type=str, default=None, help="bypass_routing_option")
    group_mosart.add_argument("--mosart_inparm-coupling_period", type=str, default=None, help="coupling_period (s)")
    group_mosart.add_argument("--mosart_inparm-decomp_option", type=str, default=None, help="decomp_option")
    group_mosart.add_argument("--mosart_inparm-delt_mosart", type=str, default=None, help="delt_mosart (s)")
    group_mosart.add_argument("--mosart_inparm-do_rtm", default=None, action=argparse.BooleanOptionalAction, help="do_rtm")
    group_mosart.add_argument("--mosart_inparm-do_rtmflood", default=None, action=argparse.BooleanOptionalAction, help="do_rtmflood")
    group_mosart.add_argument("--mosart_inparm-finidat_rtm", type=str, default=None, help="finidat_rtm")
    group_mosart.add_argument("--mosart_inparm-frivinp_rtm", type=str, default=None, help="frivinp_rtm")
    group_mosart.add_argument("--mosart_inparm-ice_runoff", default=None, action=argparse.BooleanOptionalAction, help="ice_runoff")
    group_mosart.add_argument("--mosart_inparm-qgwl_runoff_option", type=str, default=None, help="qgwl_runoff_option")
    group_mosart.add_argument("--mosart_inparm-rtmhist_fexcl1", type=str, default=None, help="rtmhist_fexcl1")
    group_mosart.add_argument("--mosart_inparm-rtmhist_fexcl2", type=str, default=None, help="rtmhist_fexcl2")
    group_mosart.add_argument("--mosart_inparm-rtmhist_fexcl3", type=str, default=None, help="rtmhist_fexcl3")
    group_mosart.add_argument("--mosart_inparm-rtmhist_fincl1", type=str, default=None, help="rtmhist_fincl1")
    group_mosart.add_argument("--mosart_inparm-rtmhist_fincl2", type=str, default=None, help="rtmhist_fincl2")
    group_mosart.add_argument("--mosart_inparm-rtmhist_fincl3", type=str, default=None, help="rtmhist_fincl3")
    group_mosart.add_argument("--mosart_inparm-rtmhist_mfilt", type=str, default=None, help="rtmhist_mfilt")
    group_mosart.add_argument("--mosart_inparm-rtmhist_ndens", type=str, default=None, help="rtmhist_ndens")
    group_mosart.add_argument("--mosart_inparm-rtmhist_nhtfrq", type=str, default=None, help="rtmhist_nhtfrq")
    group_mosart.add_argument("--mosart_inparm-smat_option", type=str, default=None, help="smat_option")

    # -------------------------------------------------------------------------
    # modelio groups (shared across all *_modelio.nml files)
    # -------------------------------------------------------------------------
    group_modelio = parser.add_argument_group("modelio", "*_modelio.nml &modelio")
    group_modelio.add_argument("--modelio-diri", type=str, default=None, help="diri (input directory)")
    group_modelio.add_argument("--modelio-diro", type=str, default=None, help="diro (output/log directory)")
    group_modelio.add_argument("--modelio-logfile", type=str, default=None, help="logfile (log filename)")

    group_pio_inparm = parser.add_argument_group("pio_inparm", "*_modelio.nml &pio_inparm")
    group_pio_inparm.add_argument("--pio_inparm-pio_netcdf_format", type=str, default=None, help="pio_netcdf_format")
    group_pio_inparm.add_argument("--pio_inparm-pio_numiotasks", type=str, default=None, help="pio_numiotasks")
    group_pio_inparm.add_argument("--pio_inparm-pio_rearranger", type=str, default=None, help="pio_rearranger")
    group_pio_inparm.add_argument("--pio_inparm-pio_root", type=str, default=None, help="pio_root")
    group_pio_inparm.add_argument("--pio_inparm-pio_stride", type=str, default=None, help="pio_stride")
    group_pio_inparm.add_argument("--pio_inparm-pio_typename", type=str, default=None, help="pio_typename")

    # Check for duplicate flags
    seen_flags = set()
    for token in sys.argv[1:]:
        if token.startswith("-"):
            if token in seen_flags:
                parser.error(f"argument {token} appears more than once")
            seen_flags.add(token)

    args = parser.parse_args()

    # --adapt processing to allow comma-separated inputs
    args.adapt = [item for s in args.adapt for item in s.split(",")]
    valid_adapt = {"drv_flds_in", "drv_in", "lnd_in", "datm_in", "mosart_in"} | set(_MODELIO_FILES)
    invalid = set(args.adapt) - valid_adapt
    if invalid:
        parser.error(f"invalid --adapt choices: {invalid}. Choose from: {valid_adapt}")

    modify_case_namelists(
        adapt=args.adapt,
        backend=args.backend,
        rundir=args.rundir,
        changelog=not args.no_changelog,
        **{k: v.replace("\\n", "\n") if isinstance(v, str) else v
           for k, v in vars(args).items()
           if k.startswith(_DRV_FLDS_IN_PREFIXES + _DRV_IN_PREFIXES + _LND_IN_PREFIXES + _DATM_IN_PREFIXES + _MOSART_IN_PREFIXES + _MODELIO_PREFIXES)},
    )
