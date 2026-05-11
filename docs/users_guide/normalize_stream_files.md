# normalize_stream_files.py

Normalizes style in eCLM DATM stream XML files.

Goal: Diffs between runs are clean and human-readable.

## What it does

The script applies one transformation to every stream file it finds:

1. **Indentation** — every element and every text-content line is
   re-indented to exactly two spaces per nesting level.  The XML
   declaration (`<?xml ... ?>`) and the root element (`<file ...>`)
   are kept at column 0.

## Files processed

The script looks for all files matching `datm.streams.*` in the target
directory. Files that are not present are silently skipped.

Typical stream file names in an eCLM run directory:

| File pattern                         | Description                        |
|--------------------------------------|------------------------------------|
| `datm.streams.txt.CLMGSWP3v1.Solar`  | Shortwave radiation stream         |
| `datm.streams.txt.CLMGSWP3v1.Precip` | Precipitation stream               |
| `datm.streams.txt.CLMGSWP3v1.TPQW`   | Temperature/pressure/humidity/wind |

## Usage

```bash
# Normalize all stream files in the current directory
python3 normalize_stream_files.py

# Normalize stream files in a specific run directory
python3 normalize_stream_files.py /path/to/rundir

# Preview which files would change without writing anything
python3 normalize_stream_files.py --dry-run [rundir]
```

### Options

| Option      | Description                                                     |
|-------------|-----------------------------------------------------------------|
| `rundir`    | Path to the directory containing stream files. Defaults to `.`  |
| `--dry-run` | Print which files would be modified without writing any changes |

## Output

For each file the script reports one of three outcomes:

```
datm.streams.txt.CLMGSWP3v1.Solar: normalized        # file was changed and written
datm.streams.txt.CLMGSWP3v1.Precip: no changes       # file was already normalized
datm.streams.txt.CLMGSWP3v1.TPQW: would be modified  # --dry-run: file would change
```
