(install)=
# Installing dwind

## Install dwind via PyPI

If you just want to use dwind and aren't developing new models, you can install it from PyPI using pip:

```bash
pip install dwind
```

## Installing from source

If you want to develop new models or contribute to dwind, you can install it from source.

### NLR-provided conda environment specification (recommended)

1. Using Git, navigate to a local target directory and clone repository:

    ```bash
    git clone https://github.com/NatLabRockies/dwind.git
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
    git clone https://github.com/NatLabRockies/dwind.git
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

## Developer Installation

Please see the [Contributor's Guide](#contributor-guide) for notes on installation steps and general
notes geared towards maintainers and contributors of the project.
