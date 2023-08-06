#!/bin/bash

# OLD way to link the rust package:
# Source: https://pyo3.rs/latest/building_and_distribution.html#manual-builds
#ln -s target/debug/librust_tetris.so rust_tetris.so

# Build the requirements files, consider the python env you're running in used to install pip-tools
pip install pip-tools
pip-compile -v requirements.in  # generate requirements.txt
pip-compile -v requirements-test.in # generate requirements-test.txt

# NEW way to link the rust package:
# Just build
python setup.py build

# Build and install all at once:
python setup.py install

# Build and Publish wheels with cibuildwheel
# https://cibuildwheel.readthedocs.io/en/stable/setup/
pip install cibuildwheel
cibuildwheel --platform linux

# Build and publish wheels with maturin
pip install maturin
maturin generate-ci github > .github/workflows/CI.yml