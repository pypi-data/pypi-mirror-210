#[macro_use]
extern crate lazy_static;
mod tetromino;
mod well;

use well::{Tetris};
use crate::well::{Well, read_game, write_game};
use pyo3::{prelude::*, wrap_pyfunction};

#[pyfunction]
pub fn create_game() -> Well {
    let mut _well: Well = Tetris::new();
    return _well;
}

#[pyfunction]
fn read_game_multithreaded() -> Well {
    return read_game();
}

#[pyfunction]
fn start_game_multithreaded() -> () {
    well::start_game_multithreaded();
}

#[pyfunction]
fn write_game_multithreaded(_well: Well) -> () {
    write_game(_well.clone());
}

/// So in python we can do: from rust_tetris import get_well
/// Example code: https://pyo3.rs/v0.14.5/module.html
/// 'static lifetimes live the duration of the program
/// Lifetime Sources:
/// https://doc.rust-lang.org/reference/lifetime-elision.html#lifetime-elision-in-functions
/// https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
#[pymodule]
#[pyo3(name = "tetris_engine_backend")]
fn setup_tetris(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(create_game, m)?)?;
    m.add_function(wrap_pyfunction!(read_game_multithreaded, m)?)?;
    m.add_function(wrap_pyfunction!(write_game_multithreaded, m)?)?;
    m.add_function(wrap_pyfunction!(start_game_multithreaded, m)?)?;
    Ok(())
}