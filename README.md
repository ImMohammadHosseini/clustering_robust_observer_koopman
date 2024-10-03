# Uncertainty Modelling and Robust Observer Synthesis using the Koopman Operator

This repository contains the companion code for [Uncertainty Modelling and
Robust Observer Synthesis using the Koopman
Operator](https://arxiv.org/abs/2410.01057). All the code required to generate
the paper's plots from raw data is included here.

The regression methods detailed in the paper are implemented using
[`pykoop`](https://github.com/decarsg/pykoop), the authors' Koopman operator
identification library.

This software relies on [`doit`](https://pydoit.org/) to automate experiment
execution and plot generation.

## Requirements

This software is compatible with Linux, macOS, and Windows. It was developed on
Arch Linux with Python 3.12.6, while the experiments used in the corresponding
paper were run on Windows 10 with Python 3.10.9. The `pykoop` library supports
any version of Python above 3.7.12. You can install Python from your package
manager or from the [official website](https://www.python.org/downloads/).

## Installation

To clone the repository, run
```sh
$ git clone git@github.com:decargroup/robust_koopman_observer.git
```

The recommended way to use Python is through a [virtual
environment](https://docs.python.org/3/library/venv.html). Create a virtual
environment (in this example, named `venv`) using
```sh
$ virtualenv venv
```
Activate the virtual environment with[^1]
```sh
$ source ./venv/bin/activate
```
To use a specific version of Python in the virtual environment, instead use
```sh
$ source ./venv/bin/activate --python <PATH_TO_PYTHON_BINARY>
```
If the virtual environment is active, its name will appear at the beginning of
your terminal prompt in parentheses:
```sh
(venv) $
```

To install the required dependencies in the virtual environment, including
`pykoop`, run
```sh
(venv) $ pip install -r ./requirements.txt
```

The LMI solver used, MOSEK, requires a license to use. You can request personal
academic license [here](https://www.mosek.com/products/academic-licenses/). You
will be emailed a license file which must be placed in `~/mosek/mosek.lic`[^2].

[^1]: On Windows, use `> \venv\Scripts\activate`.
[^2]: On Windows, place the license in `C:\Users\<USER>\mosek\mosek.lic`.

## Usage

To automatically generate all the plots used in the paper, first download the
[Quantifying Manufacturing Variation in Motor
Drives](https://doi.org/10.20383/103.01057) dataset from the Federated Research
Data Repository and place it in a directory called `dataset/` in the root of the
repository. The `raw/` and `preprocessed/` directories of the dataset should be
placed directly inside the `dataset/` directory.
The command `ls ./dataset` should show
```
example.py  preprocessed  preprocess.py  raw  README.md  requirements.txt
```

Once the dataset is downloaded, run
```sh
(venv) $ doit
```
in the repository root. This command will preprocess the raw data located in
`dataset/`, run all the required experiments, and generate figures, placing
all the results in a directory called `build/`.

To execute just one task and its dependencies, run
```sh
(venv) $ doit <TASK_NAME>
```
To see a list of all available task names, run
```sh
(venv) $ doit list --all
```
For example, to generate only the Koopman uncertainty plots, run
```sh
(venv) $ doit plot_uncertainty:koopman
```

If you have a pre-built copy of `build/` or other build products, `doit` will
think they are out-of-date and try to rebuild them. To prevent this, run
```sh
(venv) $ doit reset-dep
```
after placing the folders in the right locations. This will force `doit` to
recognize the build products as up-to-date and prevent it from trying to
re-generate them. This is useful when moving the `build/` directory between
machines.

## Repository Layout

The files and folders of the repository are described here:

| Path | Description |
| --- | --- |
| `dataset/` | Motor drive dataset must be downloaded here. |
| `build/` | Generated by `doit`. Contains all `doit` build products. |
| `figures/` | Generated by `doit`. Contains all the paper plots.|
| `dodo.py` | Describes all of `doit`'s tasks, like a `Makefile`. |
| `actions.py` | Contains the actual implementations of the `doit` tasks. |
| `obs_syn.py` | Module containing observer synthesis code. |
| `onesine.py` | Module containing sinusoidal Koopman lifting functions. |
| `tf_cover.py` | Module containing code to bound transfer function residuals. |
| `LICENSE` | Repository license |
| `requirements.txt` | Contains the required Python packages and versions. |
| `README.md` | This file. |
