# Installing dwind

## Install dwind via PyPI

If you just want to use dwind and aren't developing new models, you can install it from PyPI using pip:

```bash
pip install dwind
```

## Installing from source

If you want to develop new models or contribute to dwind, you can install it from source.

### NREL-provided conda environment specification (recommended)

1. Using Git, navigate to a local target directory and clone repository:

    ```bash
    git clone https://github.com/NREL/dwind.git
    ```

2. Navigate to `dwind`

    ```bash
    cd dwind
    ```

3. Create a conda environment and install dwind and all its dependencies

    ```bash
    conda env create -f environment.yml
    ```

An additional step can be added if additional dependencies are required, or you plan to use this
environment for development work.

- Pass `-e` for an editable developer install
- Use the extras flags `dev` to include developer and documentation build tools

This looks like the following for a developer installation:

```bash
pip install -e ".[dev]"
```

### Manual steps

1. Using Git, navigate to a local target directory and clone repository:

    ```bash
    git clone https://github.com/NREL/dwind.git
    ```

2. Navigate to `dwind`

    ```bash
    cd dwind
    ```

3. Create a new virtual environment and change to it. Using Conda Python 3.11 (choose your favorite
   supported version) and naming it 'dwind' (choose your desired name):

    ```bash
    conda create --name dwind python=3.11 -y
    conda activate dwind
    ```

4. Install dwind and its dependencies:

   - If you want to just use dwind:

       ```bash
       pip install .
       ```

    - If you also want development dependencies and documentation build tools:

       ```bash
       pip install -e ".[dev]"
       pre-commit install
       ```

## Developer Notes

Developers should add install using `pip install -e ".[dev]"` to ensure documentation testing, and
linting can be done without any additional installation steps.

Please be sure to also install the pre-commit hooks if contributing code back to the main
repository via the following. This enables a series of automated formatting and code linting
(style and correctness checking) to ensure the code is stylistically consistent.

```bash
pre-commit install
```

If a check (or multiple) fails (commit is blocked), and reformatting was done, then restage
(`git add`) your files and commit them again to see if all issues were resolved without user
intervention. If changes are required follow the suggested fix, or resolve the stated
issue(s). Restaging and committing may take multiple attempts steps if errors are unaddressed
or insufficiently addressed. Please see [pre-commit](https://pre-commit.com/),
[ruff](https://docs.astral.sh/ruff/), or [isort](https://pycqa.github.io/isort/) for more
information.

### Generating the documentation site

Once the `dev` extras are installed, and your dwind environment is activated, the documentation can
be built using the following two procedures.

1. Update the CLI documentation.

```bash
typer dwind.main utils docs --output docs/reference/cli.md --name dwind
```

2. Build the documentation site to inspect any and all changes.

```bash
jupyter-book build docs/
```

For more information on the build process in Jupyter Book, please check:
https://jupyterbook.org/en/stable/start/build.html. For more general details, please visit
https://jupyterbook.org/en/stable/intro.html.
