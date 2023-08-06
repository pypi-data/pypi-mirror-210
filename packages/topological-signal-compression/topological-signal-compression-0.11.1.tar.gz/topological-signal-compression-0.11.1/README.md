![](https://geomdata.gitlab.io/topological-signal-compression/_images/logo.gif)

A persistent homology-based signal compression method.

## Installation

### Installing from PyPI

#### Base Package

The base package can be installed via PyPI by running:

```bash
$ pip install topological-signal-compression
```

which will only install the dependencies that support the TSC compression and reconstruction algorithms.

#### [extras] Installation

There is also an option to install additional `pip` dependencies to support running:
* Counterfactual signal compression algorithms.
* Data readers.
* Visualization of persistence diagrams.
  
These extra dependencies can be installed by running:

```bash
$ pip install topological-signal-compression[extras]
```

##### WARNING: additional [extras] dependencies that *cannot* be installed with `pip`

Note, that the counterfactual compression code, specifically the Opus compression method,
also depends on installing the `opus-tools` and `ffmpeg` packages, both of which are
available for `conda` installation by running:

```bash
$ conda install -c conda-forge opus-tools
$ conda install -c conda-forge ffmpeg
```

from within a `conda` environment. There are other unix-equivalent installations that can be done to maintain
functionality, but we only test against the `conda`-based installation.

### Development Environment

To install the `conda` environment and the `jupyter` kernel with the full development environment,
clone the repo and run: 

```bash
$ cd path/to/topological-signal-compression
$ bash install.sh
```

Note, this installation script requires `mamba` (for faster installation), but you can also run the `./install.sh` script by
changing `mamba` to `conda` to remove that dependency.

To uninstall the environment and kernel, be sure to deactivate the `conda` environment, then run:

```bash
$ cd path/to/topological-signal-compression
$ bash uninstall.sh
```

## Documentation

Once the repo is cloned, `sphinx` documentation can be built after installing the `conda` environment after installing
the `[docs]` dependencies:

```bash
$ source activate tsc
$ cd path/to/topological-signal-compression
$ pip install -e .[extras,docs]
$ bash build_sphinx_docs.sh
```

It can also be built after installing the `[docs]` version of the code from `PyPI`:

```bash
$ pip install topological-signal-compression[extras,docs]
$ cd path/to/topological-signal-compression
$ bash build_sphinx_docs.sh
```

Then, open up `<path/to/topological-signal-compression>/public/index.html` in a web browser to view the documentation.

## Notebooks

All jupyter notebooks are contained in the `./notebooks` directory. These are tested to make sure they run end-to-end
without error, and can be run in the `Python (tsc)` kernel that is created by `./install.sh`. These notebooks are also
embedded in the `sphinx` documentation (see the "Documentation" section for more information).

## Testing

Testing is broken into several sets of tests. There are unit tests on the code as well as end-to-end tests on the maintained `jupyter`
notebooks in `./notebooks`.

Note, running the tests requires additional dependencies. These are built into the `conda` environment (`tsc.yml`) installed via
`install.sh`, or the testing dependencies can instead be installed by running:

```bash
$ pip install topological-signal-compression[testing]
```

Once the testing dependencies are installed, there are several options for testing.

To run the unit tests on the full `topological-signal-compression[extras]` package
(including the counterfactual compression algorithms, keep in mind the "WARNING" section above), run:

```bash
$ cd path/to/topological-signal-compression
$ pytest -c tests/pytest_tsc.ini
```

To run the unit tests on *only* the `topological-signal-compression` base installation:

```bash
$ cd path/to/topological-signal-compression
$ pytest -c tests/pytest_tsc_base_only.ini
```

To run the notebooks tests:

```bash
$ cd path/to/topological-signal-compression
$ pytest -c tests/pytest_notebooks.ini
```
