# create_ensemble_namelists.py

> **Data Assimilation only**: this script is exclusively needed for
> eCLM-PDAF experiments.  It produces the per-member namelist files
> that PDAF expects to find for each ensemble member.  It is not
> required for standard (single-instance) eCLM runs.

Creates per-ensemble-member copies of all eCLM namelist and stream
files from a single set of base namelists.

## What it does

Starting from the base namelist files in the run directory, the script
writes one set of ensemble-specific files for every member `1 .. N`.
Each output filename carries a four-digit zero-padded member index as
a suffix (`_NNNN`).

The following modifications are applied per file type:

| Output file              | Source              | Modification                                                                                                      |
|--------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------|
| `{mod}_modelio.nml_NNNN` | `{mod}_modelio.nml` | `logfile` gets `_NNNN` inserted before `.log`                                                                     |
| `datm_in_NNNN`           | `datm_in`           | Each stream filename in `shr_strdata_nml:streams` gets `_NNNN` inserted before `.txt`                             |
| `lnd_in_NNNN`            | `lnd_in`            | Unchanged copy; optionally `clm_inparm:fsurdat` (5-digit), `finidat` (after `.clm2`), or `paramfile` get a suffix |
| `mosart_in_NNNN`         | `mosart_in`         | Unchanged copy                                                                                                    |
| `datm.streams_NNNN.*`    | `datm.streams.*`    | `fieldInfo/filePath` is redirected from `./forcings` to `./forcings/real_NNNNN`                                   |

The `{mod}` components processed for modelio files are:
`atm`, `esp`, `glc`, `ice`, `lnd`, `ocn`, `rof`, `wav`, `cpl`.

## Usage

```bash
# Create namelists for 96 ensemble members (default) in the current directory
python3 create_ensemble_namelists.py

# Specify run directory and ensemble size
python3 create_ensemble_namelists.py \
    --rundir /path/to/rundir \
    --num_ensemble 50

# Also add per-member suffix to the surface data file path
python3 create_ensemble_namelists.py \
    --rundir /path/to/rundir \
    --num_ensemble 50 \
    --suffix-fsurdat

# Add per-member suffix to the initial conditions file
python3 create_ensemble_namelists.py \
    --rundir /path/to/rundir \
    --num_ensemble 50 \
    --suffix-finidat

# Add per-member suffix to the CLM parameter file
python3 create_ensemble_namelists.py \
    --rundir /path/to/rundir \
    --num_ensemble 50 \
    --suffix-paramfile
```

### Options

| Option                 | Description                                                                                      |
|------------------------|--------------------------------------------------------------------------------------------------|
| `-r`, `--rundir`       | Directory containing the base namelist files. Defaults to `.`                                    |
| `-n`, `--num_ensemble` | Number of ensemble members to generate. Defaults to `96`                                         |
| `-b`, `--backend`      | Namelist backend: `re` (default, regexp-based) or `f90nml`                                       |
| `-f`, `--forcings-dir` | Forcings directory used in stream file `fieldInfo/filePath` entries. Defaults to `./forcings`    |
| `--suffix-fsurdat`     | Add a five-digit member suffix to `clm_inparm:fsurdat` in `lnd_in_NNNN`                          |
| `--suffix-finidat`     | Add a four-digit member suffix to `clm_inparm:finidat` in `lnd_in_NNNN`, inserted after `.clm2`  |
| `--suffix-paramfile`   | Add a four-digit member suffix to `clm_inparm:paramfile` in `lnd_in_NNNN`, inserted before `.nc` |

## Expected run directory layout

The script reads the following base files from `--rundir` and must be
called **after** the base namelists have been set up (e.g. with
`modify_case_namelists.py`):

```
rundir/
  atm_modelio.nml   cpl_modelio.nml   esp_modelio.nml
  glc_modelio.nml   ice_modelio.nml   lnd_modelio.nml
  ocn_modelio.nml   rof_modelio.nml   wav_modelio.nml
  datm_in
  lnd_in
  mosart_in
  datm.streams.txt.*   (one file per DATM stream)
```

## Output

The script prints a running status line and exits after all members are
written:

```
[Done with ensemble member: 50]
```

Output files are written into the same directory as the base namelists:

```
rundir/
  lnd_modelio.nml_0001  lnd_modelio.nml_0002  ...  lnd_modelio.nml_0050
  datm_in_0001          datm_in_0002          ...  datm_in_0050
  lnd_in_0001           lnd_in_0002           ...  lnd_in_0050
  mosart_in_0001        mosart_in_0002        ...  mosart_in_0050
  datm.streams_0001.txt.*  datm.streams_0002.txt.*  ...
  ...
```
