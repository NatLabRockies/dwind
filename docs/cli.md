# CLI

**Usage**:

```console
$ dwind [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `run`: Run a dwind analysis via sbatch or in an...
* `debug`: Help identify issues with analyses that...
* `collect`: Gather results from a run or rerun analysis.

## `dwind run`

Run a dwind analysis via sbatch or in an interactive session.

**Usage**:

```console
$ dwind run [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `hpc`: Run dwind via the HPC multiprocessing...
* `interactive`: Run dwind locally, or via an interactive...
* `config`: Run dwind via the HPC multiprocessing...
* `chunk`: Run a chunk of a dwind model.

### `dwind run hpc`

Run dwind via the HPC multiprocessing interface.

**Usage**:

```console
$ dwind run hpc [OPTIONS] LOCATION SECTOR:{fom|btm} SCENARIO:{baseline|metering|billing|highrecost|lowrecost} YEAR REPOSITORY NODES ALLOCATION MEMORY WALLTIME FEATURE ENV MODEL_CONFIG DIR_OUT
```

**Arguments**:

* `LOCATION`: The state, state_county, or priority region to run.  [required]
* `SECTOR:{fom|btm}`: One of fom (front of meter) or btm (back-of-the-meter).  [required]
* `SCENARIO:{baseline|metering|billing|highrecost|lowrecost}`: The scenario to run (baseline is the current only option).  [required]
* `YEAR`: The assumption year for the analysis. Options are 2022, 2024, and 2025.  [required]
* `REPOSITORY`: Path to the dwind repository to use when running the model.  [required]
* `NODES`: Number of HPC nodes or CPU nodes to run on. -1 indicates 75% of CPU limit.  [required]
* `ALLOCATION`: HPC allocation name.  [required]
* `MEMORY`: Node memory, in GB (HPC only).  [required]
* `WALLTIME`: Node walltime request, in hours.  [required]
* `FEATURE`: Additional flags for the SLURM job, using formatting such as --qos=high or --depend=.  [required]
* `ENV`: The path to the dwind Python environment that should be used to run the model.  [required]
* `MODEL_CONFIG`: Complete file name and path of the model configuration file  [required]
* `DIR_OUT`: Path to where the chunked outputs should be saved.  [required]

**Options**:

* `--stdout-path TEXT`: The path to write stdout logs.
* `-c, --combine / -C, --no-combine`: Automatically combine the chunked results after analysis completion.  [default: combine]
* `-ra, --remove-agent-chunks / -RA, --no-remove-agent-chunks`: Delete the temporary agent chunk files.  [default: remove-agent-chunks]
* `-rr, --remove-results-chunks / -RR, --no-remove-results-chunks`: Delete the chunked results files. Ignored if --combine is not passed.  [default: remove-results-chunks]
* `--help`: Show this message and exit.

### `dwind run interactive`

Run dwind locally, or via an interactive session where a SLURM job is not scheduled.

**Usage**:

```console
$ dwind run interactive [OPTIONS] LOCATION SECTOR:{fom|btm} SCENARIO:{baseline|metering|billing|highrecost|lowrecost} YEAR DIR_OUT REPOSITORY MODEL_CONFIG
```

**Arguments**:

* `LOCATION`: The state, state_county, or priority region to run.  [required]
* `SECTOR:{fom|btm}`: One of fom (front of meter) or btm (back-of-the-meter).  [required]
* `SCENARIO:{baseline|metering|billing|highrecost|lowrecost}`: The scenario to run, such as &#x27;baseline&#x27;.  [required]
* `YEAR`: The year basis of the scenario.  [required]
* `DIR_OUT`: save path  [required]
* `REPOSITORY`: Path to the dwind repository to use when running the model.  [required]
* `MODEL_CONFIG`: Complete file name and path of the model configuration file  [required]

**Options**:

* `--kwargs TEXT`: Do not pass arguments here, this is for internal overflow only.  [required]
* `--help`: Show this message and exit.

### `dwind run config`

Run dwind via the HPC multiprocessing interface from a configuration file.

**Usage**:

```console
$ dwind run config [OPTIONS] CONFIG_PATH
```

**Arguments**:

* `CONFIG_PATH`: Path to configuration TOML with run and model parameters.  [required]

**Options**:

* `--use-hpc / --no-use-hpc`: Run via sbatch on the HPC (--use-hpc) or interactively (--no-use-hpc).  [default: use-hpc]
* `-c, --combine / -C, --no-combine`: Automatically combine the chunked results after analysis completion. Ignored if --no-use-hpc.  [default: combine]
* `-ra, --remove-agent-chunks / -RA, --no-remove-agent-chunks`: Delete the temporary agent chunk files. Ignored if --no-use-hpc.  [default: remove-agent-chunks]
* `-rr, --remove-results-chunks / -RR, --no-remove-results-chunks`: Delete the chunked results files. Ignored if --combine is not passed or --no-use-hpc is passed.  [default: remove-results-chunks]
* `--help`: Show this message and exit.

### `dwind run chunk`

Run a chunk of a dwind model. Internal only, do not run outside the context of a
chunked analysis or debugging.

**Usage**:

```console
$ dwind run chunk [OPTIONS] CHUNK_IX LOCATION SECTOR:{fom|btm} SCENARIO:{baseline|metering|billing|highrecost|lowrecost} YEAR OUT_PATH REPOSITORY MODEL_CONFIG
```

**Arguments**:

* `CHUNK_IX`: Chunk number/index. Used for logging.  [required]
* `LOCATION`: The state, state_county, or priority region to run.  [required]
* `SECTOR:{fom|btm}`: One of fom (front of meter) or btm (back-of-the-meter).  [required]
* `SCENARIO:{baseline|metering|billing|highrecost|lowrecost}`: The scenario to run, such as baseline.  [required]
* `YEAR`: The year basis of the scenario.  [required]
* `OUT_PATH`: save path  [required]
* `REPOSITORY`: Path to the dwind repository to use when running the model.  [required]
* `MODEL_CONFIG`: Complete file name and path of the model configuration file  [required]

**Options**:

* `--help`: Show this message and exit.

## `dwind debug`

Help identify issues with analyses that were run.

**Usage**:

```console
$ dwind debug [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `job-summary`: Print a table summary of the provided job...
* `missing-agents-from-chunks`: Compare the agent &quot;gid&quot; field between the...
* `missing-agents`: Compare the agent &quot;gid&quot; field between the...

### `dwind debug job-summary`

Print a table summary of the provided job id(s) and their final run status.

**Usage**:

```console
$ dwind debug job-summary [OPTIONS] JOBS...
```

**Arguments**:

* `JOBS...`: Job ID(s) to check for the final run status.  [required]

**Options**:

* `-c, --chunks INTEGER`: Corresponding chunk indexes for each job ID.
* `--help`: Show this message and exit.

### `dwind debug missing-agents-from-chunks`

Compare the agent &quot;gid&quot; field between the chunked agents and results files, and save the
missing chunk index and agent gid as a 1-column CSV file.

**Usage**:

```console
$ dwind debug missing-agents-from-chunks [OPTIONS] DIR_OUT
```

**Arguments**:

* `DIR_OUT`: Path to where the chunked outputs were saved. Should match the inputs to the run command.  [required]

**Options**:

* `--chunks INTEGER`: If used, specify chunked indicies to compare.
* `--help`: Show this message and exit.

### `dwind debug missing-agents`

Compare the agent &quot;gid&quot; field between the chunked agents and results files, and save the
missing chunk index and agent gid as a 2-column CSV file.

**Usage**:

```console
$ dwind debug missing-agents [OPTIONS] AGENTS_FILE RESULTS_FILE DIR_OUT
```

**Arguments**:

* `AGENTS_FILE`: Full file path and name of the agents file.  [required]
* `RESULTS_FILE`: Full file path and name of the results file.  [required]
* `DIR_OUT`: Full file path and name for where to save the list of missing agent gids.  [required]

**Options**:

* `--help`: Show this message and exit.

## `dwind collect`

Gather results from a run or rerun analysis.

**Usage**:

```console
$ dwind collect [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `combine-chunks`: Combine the results of a multi-job run...
* `cleanup-agents`: Deletes the temporary agent chunk files...
* `cleanup-results`: Deletes the chunked results files...

### `dwind collect combine-chunks`

Combine the results of a multi-job run based on the run&#x27;s TOML configuration. Please note
this has the potential to combine multiple runs as it does not respect the jobs ran during a
single cycle.

**Usage**:

```console
$ dwind collect combine-chunks [OPTIONS] DIR_OUT
```

**Arguments**:

* `DIR_OUT`: Path to where the chunked outputs should be saved. Should be the same that was passed to the run command.  [required]

**Options**:

* `-f, --file-name TEXT`: Custom filename, without the extension (e.g. .pqt), for the results data.
* `-rr, --remove-results-chunks / -RR, --no-remove-results-chunks`: Delete the individual chunk files after saving the combined results.  [default: remove-results-chunks]
* `--help`: Show this message and exit.

### `dwind collect cleanup-agents`

Deletes the temporary agent chunk files generated at runtime.

Args:
    dir_out (str): The base output directory, which should be the same as that passed to the
        run command.

**Usage**:

```console
$ dwind collect cleanup-agents [OPTIONS] DIR_OUT
```

**Arguments**:

* `DIR_OUT`: Path to where the chunked agents were saved. Should be the same that was passed to the run command.  [required]

**Options**:

* `--help`: Show this message and exit.

### `dwind collect cleanup-results`

Deletes the chunked results files generated at runtime.

Args:
    dir_out (str): The base output directory, which should be the same as that passed to the
        run command.

**Usage**:

```console
$ dwind collect cleanup-results [OPTIONS] DIR_OUT
```

**Arguments**:

* `DIR_OUT`: Path to where the results agents were saved. Should be the same that was passed to the run command.  [required]

**Options**:

* `--help`: Show this message and exit.
