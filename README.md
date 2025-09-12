# Distributed Wind Generation Model (dWind)

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![PyPI - Version](https://img.shields.io/pypi/v/dwind)
[![Jupyter Book](https://jupyterbook.org/badge.svg)](https://nrel.github.io/dwind)

[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


Please note that at this time the model can only be run on NREL's Kestrel HPC system. Though a
savvy user could recreate our data in their own computing environment and update the
internal pointers in the example configuration at `examples/larimer_county_btm_baseline_2025.toml`
and `examples/model_config.toml`.

## Installing dwind

1. Install Anaconda or Miniconda (recommended) if not already installed.
2. Clone the repository

   ```bash
   git clone https://github.com/NREL/dwind.git
   ```

3. Navigate to the dwind repository.

   ```bash
   cd /path/to/dwind
   ```

4. Create your dwind environment using our recommended settings and all required dependencies.

    ```bash
    conda env create -f environment.yml
    ```

## Running

### Configuring

`dWind` relies on 2 configuration files: 1) a system-wise setting that can be shared among a team,
and 2) a run-specific configuration file. Both will be described below.

#### Primary model configuration

The primary model configuration should look exactly like (or be compatible with)
`examples/model_config.toml` to ensure varying fields are read correctly throughout the model.

Internally, `dWind` is able to convert the following data to adhere to internal usage:
- Any field with "DIR" is converted to a Python `pathlib.Path` object for robust file handling
- SQL credentials and constructor strings are automatically formed in the `[sql]` table for easier
  construction of generic connection strings. Specifically the `{USER}` and `{PASSWORD}` fields
  get replaced with their corresponding setting in the same table.

`Configuration`, the primary class handling this data allows for dot notation and dictionary-style
attribute calling at all levels of nesting. This means, `config.pysam.outputs.btm` and
`config.pysam.outputs["btm"]` are equivalent. This makes for more intuitive dynamic attribute
fetching when updating the code for varying cases.

#### Run configuration

The run-specific configuration should look like `examples/larimer_county_btm_baseline_2025.toml`,
which controls all the dynamic model settings, HPC configurations, and a pointer to the primary
model configuration described above.

### Run the model

`dwind` has a robust CLI interface allowing for the usage of `python path/to/dwind/dwind/main.py` or
by directly calling`dwind`. For more details on using the CLI, use the `--help` flag, or visit our
CLI documentation page https://nrel.github.io/dwind/cli.html

To run the model, it is recommended to use the following workflow from your analysis folder.

1. Start a new `screen` session on Kestrel.

   ```bash
   screen -S <analysis-name>
   ```

2. Load your conda environment with dwind installed.

   ```bash
   module load conda
   conda activate <env_name>
   ```

3. Navigate to your analysis folder if your relative data locations in your run configuration are
   relative to the analysis folder.

   ```bash
   cd /path/to/analysis/location
   ```

4. Run the model.

   ```bash
   dwind run config examples/larimer_county_btm_baseline_2025.toml
   ```

5. Disconnect your screen `Ctrl` + `a` + `d` and wait for the analysis to complete and view your
   results.
