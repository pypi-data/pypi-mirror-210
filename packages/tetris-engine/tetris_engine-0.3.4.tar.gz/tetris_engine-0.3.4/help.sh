#!/bin/bash

# the name of the module must match the name of the .so or .pyd file in target/debug or target/release
# https://pyo3.rs/v0.14.5/module.html
# https://pyo3.rs/v0.4.1/
# https://pyo3.rs/main/building_and_distribution.html#manual-builds

# https://pyo3.rs/v0.4.1/
rustup target list
rustup target add <specific target from list>

cargo build --lib --target x86_64-apple-darwin
