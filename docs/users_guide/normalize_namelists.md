# normalize_namelists.py

Normalizes style in eCLM namelist files so that diffs between runs are
clean and human-readable.

## What it does

The script applies four transformations to every namelist file it
finds:

1. **Indentation** - lines inside a `&group ... /` block are re-indented
   to exactly two spaces. Group header (`&group`) and closing (`/`)
   lines are left as-is.

2. **Quote style** - string values delimited by double quotes are
   rewritten to use single quotes (`"value"` -> `'value'`). The value
   content is never modified.

3. **Continuation alignment** - continuation lines of multi-line values are
   indented to align with the value start on the `key = value` line above:
   ```
     hist_fincl1 = 'SOILWATER_10CM', 'H2OSOI',
                   'SOILLIQ', 'SOILICE'
   ```

4. **Equals-sign spacing** - exactly one space is placed before and after
   the `=` sign in every `key = value` entry (`key=value` and
   `key  =  value` are both rewritten to `key = value`).

Lines outside a group (blank lines, comment blocks appended by
`modify_case_namelists.py`, etc.) are passed through unchanged.

## Files processed

The script looks for the following files in the target directory:

| File                                                | Description                 |
|-----------------------------------------------------|-----------------------------|
| `drv_flds_in`                                       | Driver field list           |
| `drv_in`                                            | Driver namelist             |
| `lnd_in`                                            | Land model namelist         |
| `datm_in`                                           | Data atmosphere namelist    |
| `mosart_in`                                         | River routing namelist      |
| `{atm,cpl,esp,glc,ice,lnd,ocn,rof,wav}_modelio.nml` | Per-component I/O namelists |

Files that are not present in the directory are silently skipped.

## Usage

```bash
# Normalize all namelist files in the current directory
python3 normalize_namelists.py

# Normalize files in a specific run directory
python3 normalize_namelists.py /path/to/rundir

# Preview which files would change without writing anything
python3 normalize_namelists.py --dry-run [rundir]
```

### Options

| Option      | Description                                                      |
|-------------|------------------------------------------------------------------|
| `rundir`    | Path to the directory containing namelist files. Defaults to `.` |
| `--dry-run` | Print which files would be modified without writing any changes  |

## Output

For each file the script reports one of three outcomes:

```
lnd_in: normalized        # file was changed and written
drv_in: no changes        # file was already normalized
datm_in: would be modified  # --dry-run: file would change
```
