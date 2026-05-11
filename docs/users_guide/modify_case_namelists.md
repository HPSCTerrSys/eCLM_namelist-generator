# modify_case_namelists.py

Modifies key-value entries in eCLM case namelist files.

## What it does

The script rewrites individual namelist keys in one or more eCLM case
namelist files. Only the keys targeted by the supplied options are
changed; all other content is left untouched.

After modifying each file the script appends a comment block recording
the timestamp and the full command that was run (suppressed with
`--no-changelog`):

```fortran
!#--------------------------------------------------------------------------------------------------------------------------
!# lnd_in:: Modified by modify_case_namelists.py on 2024-07-01 09:15:00
!# Command: modify_case_namelists.py --rundir /path/to/rundir --clm_inparm-finidat my_restart.nc
!#--------------------------------------------------------------------------------------------------------------------------
```

## Files and option groups

Options are organised by the file and namelist group they target. The
prefix of each option flag identifies both:

| Option prefix        | File            | Namelist group                |
|----------------------|-----------------|-------------------------------|
| `--megan-`           | `drv_flds_in`   | `&megan_emis_nl`              |
| `--timemgr-`         | `drv_in`        | `&seq_timemgr_inparm`         |
| `--infodata-`        | `drv_in`        | `&seq_infodata_inparm`        |
| `--driver-`          | `drv_in`        | `&cime_driver_inst`           |
| `--pes-`             | `drv_in`        | `&cime_pes`                   |
| `--esmf-`            | `drv_in`        | `&esmf_inparm`                |
| `--pio-`             | `drv_in`        | `&pio_default_inparm`         |
| `--prof-`            | `drv_in`        | `&prof_inparm`                |
| `--cplflds-`         | `drv_in`        | `&seq_cplflds_inparm`         |
| `--flux_mct-`        | `drv_in`        | `&seq_flux_mct_inparm`        |
| `--clm_inparm-`      | `lnd_in`        | `&clm_inparm`                 |
| `--ndepdyn-`         | `lnd_in`        | `&ndepdyn_nml`                |
| `--soilhydro-`       | `lnd_in`        | `&soilhydrology_inparm`       |
| `--soilwater-`       | `lnd_in`        | `&soilwater_movement_inparm`  |
| `--canopyhydro-`     | `lnd_in`        | `&clm_canopyhydrology_inparm` |
| `--atm2lnd-`         | `lnd_in`        | `&atm2lnd_inparm`             |
| `--datm_nml-`        | `datm_in`       | `&datm_nml`                   |
| `--shr_strdata_nml-` | `datm_in`       | `&shr_strdata_nml`            |
| `--mosart_inparm-`   | `mosart_in`     | `&mosart_inparm`              |
| `--modelio-`         | `*_modelio.nml` | `&modelio`                    |
| `--pio_inparm-`      | `*_modelio.nml` | `&pio_inparm`                 |

Run `python3 modify_case_namelists.py --help` for the complete list of
available keys within each group.

## Usage

```bash
# Set run period and CLM initial conditions
python3 modify_case_namelists.py \
    --rundir /path/to/rundir \
    --timemgr-start_ymd 20220101 \
    --timemgr-stop_ymd  20221231 \
    --clm_inparm-finidat my_restart.nc

# Change output directory in all modelio files
python3 modify_case_namelists.py \
    --rundir /path/to/rundir \
    --adapt lnd_modelio.nml atm_modelio.nml \
    --modelio-diro /scratch/logs

# Modify only lnd_in, skip the changelog comment
python3 modify_case_namelists.py \
    --rundir /path/to/rundir \
    --adapt lnd_in \
    --no-changelog \
    --clm_inparm-spinup_state 1
```

### General options

| Option            | Description                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------------|
| `-r`, `--rundir`  | Directory containing the namelist files. Defaults to `.`                                      |
| `-a`, `--adapt`   | Which files to modify (space- or comma-separated). Default: `drv_in lnd_in datm_in mosart_in` |
| `-b`, `--backend` | Namelist backend: `re` (default, regexp-based) or `f90nml`                                    |
| `--no-changelog`  | Do not append the modification comment block to modified files                                |

### Commonly used keys

**Run period** (`--timemgr-`)

| Option                     | Namelist key     | Description                            |
|----------------------------|------------------|----------------------------------------|
| `--timemgr-start_ymd`      | `start_ymd`      | Start date (`YYYYMMDD`)                |
| `--timemgr-stop_ymd`       | `stop_ymd`       | Stop date (`YYYYMMDD`)                 |
| `--timemgr-stop_n`         | `stop_n`         | Run length (number of units)           |
| `--timemgr-stop_option`    | `stop_option`    | Run length unit (`nyears`, `ndays`, …) |
| `--timemgr-restart_n`      | `restart_n`      | Restart interval (number)              |
| `--timemgr-restart_option` | `restart_option` | Restart interval unit                  |
| `--timemgr-calendar`       | `calendar`       | Calendar type                          |
| `--timemgr-atm_cpl_dt`     | `atm_cpl_dt`     | ATM coupling time step (s)             |
| `--timemgr-lnd_cpl_dt`     | `lnd_cpl_dt`     | LND coupling time step (s)             |

**Land model** (`--clm_inparm-`)

| Option                      | Namelist key   | Description                                |
|-----------------------------|----------------|--------------------------------------------|
| `--clm_inparm-finidat`      | `finidat`      | Initial conditions file                    |
| `--clm_inparm-fsurdat`      | `fsurdat`      | Surface data file                          |
| `--clm_inparm-fatmlndfrc`   | `fatmlndfrc`   | Domain file                                |
| `--clm_inparm-paramfile`    | `paramfile`    | CLM parameter file                         |
| `--clm_inparm-dtime`        | `dtime`        | CLM time step (s)                          |
| `--clm_inparm-spinup_state` | `spinup_state` | Spinup mode (0: normal, 1: AD, 2: post-AD) |
| `--clm_inparm-hist_nhtfrq`  | `hist_nhtfrq`  | History write frequency                    |
| `--clm_inparm-hist_mfilt`   | `hist_mfilt`   | Max frames per history file                |
| `--clm_inparm-hist_fincl1`  | `hist_fincl1`  | History field list (Fortran list string)   |

**DATM streams** (`--shr_strdata_nml-`)

| Option                         | Namelist key | Description                            |
|--------------------------------|--------------|----------------------------------------|
| `--shr_strdata_nml-streams`    | `streams`    | Stream file list (Fortran list string) |
| `--shr_strdata_nml-domainfile` | `domainfile` | DATM domain file                       |

**Model I/O** (`--modelio-`, `--pio_inparm-`)

| Option                        | Namelist key     | Description                           |
|-------------------------------|------------------|---------------------------------------|
| `--modelio-diri`              | `diri`           | Input directory                       |
| `--modelio-diro`              | `diro`           | Output/log directory                  |
| `--modelio-logfile`           | `logfile`        | Log filename                          |
| `--pio_inparm-pio_typename`   | `pio_typename`   | PIO I/O type (`netcdf`, `pnetcdf`, …) |
| `--pio_inparm-pio_numiotasks` | `pio_numiotasks` | Number of PIO I/O tasks               |

### Multi-value keys

Some keys hold comma-separated Fortran list values (e.g. `hist_fincl1`,
`streams`).  Pass the entire Fortran list string as a single quoted
argument:

```bash
--clm_inparm-hist_fincl1 "'SOILWATER_10CM', 'H2OSOI', 'SOILLIQ'"
```
