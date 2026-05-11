# modify_stream_files.py

Modifies field values inside eCLM DATM stream XML files.

## What it does

The script rewrites the text content of specific XML elements in one
or more stream files. Only the elements targeted by the supplied
options are changed; everything else is left untouched.

Supported elements:

| Option                       | XML path                      |
|------------------------------|-------------------------------|
| `--datasource`               | `<dataSource>`                |
| `--domaininfo-filepath`      | `<domainInfo><filePath>`      |
| `--domaininfo-filenames`     | `<domainInfo><fileNames>`     |
| `--domaininfo-variablenames` | `<domainInfo><variableNames>` |
| `--fieldinfo-filepath`       | `<fieldInfo><filePath>`       |
| `--fieldinfo-filenames`      | `<fieldInfo><fileNames>`      |
| `--fieldinfo-variablenames`  | `<fieldInfo><variableNames>`  |
| `--fieldinfo-offset`         | `<fieldInfo><offset>`         |

## Usage

```bash
python3 modify_stream_files.py \
    --rundir /path/to/rundir \
    --file user_datm.streams.txt.CLMCRUNCEPv7.Solar \
    --domaininfo-filepath ./input_clm \
    --domaininfo-filenames domain.lnd.DE-RuS.240717.nc \
    --fieldinfo-filepath ./forcings \
    --fieldinfo-filenames "2022-01.nc\n2022-02.nc\n2022-03.nc"
```

Multiple stream files can be modified in one call by listing them after
`--file`:

```bash
python3 modify_stream_files.py \
    --rundir /path/to/rundir \
    --file user_datm.streams.txt.CLMCRUNCEPv7.Solar \
          user_datm.streams.txt.CLMCRUNCEPv7.Precip \
    --fieldinfo-filepath ./forcings
```

### Options

| Option                       | Description                                                     |
|------------------------------|-----------------------------------------------------------------|
| `-r`, `--rundir`             | Directory containing the stream files. Defaults to `.`          |
| `-f`, `--file`               | One or more stream filenames to modify (relative to `--rundir`) |
| `--datasource`               | `<dataSource>` text content                                     |
| `--domaininfo-filepath`      | `<domainInfo><filePath>` — directory of the domain file         |
| `--domaininfo-filenames`     | `<domainInfo><fileNames>` — domain filename(s)                  |
| `--domaininfo-variablenames` | `<domainInfo><variableNames>` — variable name mapping pairs     |
| `--fieldinfo-filepath`       | `<fieldInfo><filePath>` — directory of the forcing/field files  |
| `--fieldinfo-filenames`      | `<fieldInfo><fileNames>` — field filename(s)                    |
| `--fieldinfo-variablenames`  | `<fieldInfo><variableNames>` — variable name mapping pairs      |
| `--fieldinfo-offset`         | `<fieldInfo><offset>`                                           |

### Multi-line values

Use `\n` in any string value to insert a newline in the output.  This
is the standard way to supply a list of files to
`--fieldinfo-filenames` or `--domaininfo-filenames`:

```bash
--fieldinfo-filenames "  2022-01.nc\n  2022-02.nc\n  2022-03.nc"
```

produces:

```xml
<fileNames>
  2022-01.nc
  2022-02.nc
  2022-03.nc
</fileNames>
```
