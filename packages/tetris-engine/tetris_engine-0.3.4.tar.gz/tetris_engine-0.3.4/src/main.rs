#[macro_use]
extern crate lazy_static;
use std::borrow::{Borrow, BorrowMut};
use std::rc::Rc;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use crate::well::{Tetris, Well};

mod tetromino;
mod well;


fn main() {
    let mut t: Well = Tetris::new();
    t.setup();
    t.run_game();
}


