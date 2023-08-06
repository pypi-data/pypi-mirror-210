use std::cmp::{max, min};
use rand::Rng;
use crate::well::{WELL_WIDTH, WELL_HEIGHT};
use pyo3::prelude::*;

pub const TETROMINO_WIDTH: usize = 4;
pub const TETROMINO_HEIGHT: usize = 4;


/// ## Arguments
///     * area The grid (e.g. 4x4) in which the tetromino will be drawn
///     * x (height) position in the well coordinate plane
///     * y (width) position in the well coordinate plane
/// ## Resources
///     * https://www.youtube.com/watch?v=8OK8_tHeCIA
#[pyclass]
pub struct Tetromino {
    #[pyo3(get)]
    pub area: [[i32; TETROMINO_WIDTH]; TETROMINO_HEIGHT],
    #[pyo3(get)]
    pub x: usize,
    #[pyo3(get)]
    pub y: usize,
    #[pyo3(get)]
    pub name: String,
}

impl Clone for Tetromino {
    fn clone(&self) -> Self {
        Tetromino {
            area: self.area.clone(),
            x: self.x.clone(),
            y: self.y.clone(),
            name: self.name.clone(),
        }
    }
}

impl Tetromino {
    pub fn rotate(&mut self, reverse: bool) -> () {
        if reverse {
            for _ in 0..3 {
                rotate(self);
            }
        } else {
            rotate(self);
        }
        self.move_to_top_left();
    }

    /// Gets (min_x, max_x, min_y, max_y) the current tetromino piece fills
    /// in the current well coordinate plane
    /// May want to deprecate this
    pub fn get_xy_min_max(&mut self) -> (usize, usize, usize, usize) {
        let mut min_x: usize = TETROMINO_HEIGHT;
        let mut max_x: usize = 0;
        let mut min_y: usize = TETROMINO_WIDTH;
        let mut max_y: usize = 0;
        for i in 0..TETROMINO_HEIGHT {
            for j in 0..TETROMINO_WIDTH {
                if self.area[i][j] == 1 {
                    min_x = min(min_x, i);
                    max_x = max(max_x, i);
                    min_y = min(min_y, j);
                    max_y = max(max_y, j);
                }
            }
        }
        return (min_x, max_x, min_y, max_y);
    }

    fn log_tetromino(&self) -> () {
        log::info!("Tetromino: ");
        for x in 0..self.area.len() {
            log::info!("{:?}", self.area[x]);
        }

    }

    /// Iterate over each point in the tetromino grid that is active
    /// if that point is active, add dx and dy to it, then check if the new position lands
    /// in a spot in the grid that is already active
    /// only the grid's walls and stuck tetrominos are marked as 1
    /// empty spaces are left as 0
    /// The current tetromino is marked with 2's
    pub fn will_collide(&mut self, grid: [[i32; WELL_WIDTH]; WELL_HEIGHT], dx: i32, dy: i32) -> bool {
        self.log_tetromino();
        for _y in 0..TETROMINO_HEIGHT {
            for _x in 0..TETROMINO_WIDTH {
                if self.area[_y][_x] == 1 {
                    let xx: i32 = self.x as i32 + _x as i32 + dx;
                    let yy: i32 = self.y as i32 + _y as i32 + dy;
                    if grid[yy as usize][xx as usize] == 1 {
                        log::info!("({},{}) will collide", xx, yy);
                        return true;
                    } else {
                        log::info!("({},{}) will not collide", xx, yy);
                    }
                }
            }
        }
        return false;
    }

    /// Returns true if the tetromino is stuck in the grid or false if it can still move
    pub fn is_stuck(&mut self, grid: [[i32; WELL_WIDTH]; WELL_HEIGHT]) -> bool {
        return self.will_collide(grid, 0, 1);
    }

    /// Sticks the tetromino to the grid
    pub fn stick_to_grid(&mut self, grid: &mut [[i32; WELL_WIDTH]; WELL_HEIGHT]) -> () {
        for _y in 0..TETROMINO_HEIGHT {
            for _x in 0..TETROMINO_WIDTH {
                if self.area[_y][_x] == 1 {
                    let xx: i32 = self.x as i32 + _x as i32;
                    let yy: i32 = self.y as i32 + _y as i32;
                    grid[yy as usize][xx as usize] = 1;
                }
            }
        }
    }

    fn move_to_top_left(&mut self) {
        while self.is_row_empty(0) {
            self.shift_up();
        }
        while self.is_column_empty(0) {
            self.shift_left();
        }
    }

    fn is_row_empty(&self, i: usize) -> bool {
        assert!(i < TETROMINO_HEIGHT);
        for j in 0..TETROMINO_WIDTH {
            if self.area[i][j] != 0 {
                return false;
            }
        }
        return true;
    }

    fn is_column_empty(&self, j: usize) -> bool {
        assert!(j < TETROMINO_WIDTH);
        for i in 0..TETROMINO_HEIGHT {
            if self.area[i][j] != 0 {
                return false;
            }
        }
        return true;
    }

    fn shift_up(&mut self) {
        for i in 0..TETROMINO_HEIGHT {
            for j in 0..TETROMINO_WIDTH {
                if i < TETROMINO_HEIGHT - 1 {
                    self.area[i][j] = self.area[i + 1][j];
                } else {
                    self.area[i][j] = 0;
                }
            }
        }
    }

    fn shift_left(&mut self) {
        for i in 0..TETROMINO_HEIGHT {
            for j in 0..TETROMINO_WIDTH {
                if j < TETROMINO_WIDTH - 1 {
                    self.area[i][j] = self.area[i][j+1];
                } else {
                    self.area[i][j] = 0;
                }
            }
        }

    }
}

impl Default for Tetromino {
    fn default() -> Tetromino {
        Tetromino {
            area: [[1,0,0,0],
                   [1,0,0,0],
                   [1,0,0,0],
                   [1,0,0,0]],
            x: WELL_WIDTH / 2, // horizontal starting position
            y: 0, // height
            name: "straight".to_string(),
        }
    }
}

/// Rotate 90 degrees clockwise
fn rotate(t: &mut Tetromino) -> () {
    let n = t.area.len();
    let m = t.area[0].len();

    // transpose across left to right diagonal
    for i in 0..n {
        for j in i..m {
            let tmp = t.area[i][j];
            t.area[i][j] = t.area[j][i];
            t.area[j][i] = tmp;
        }
    }
    // reverse each row
    // same as a flip w/ respect to middle column
    for i in 0..n {
        t.area[i].reverse();
    }
}

/// Rotate 90 degrees clockwise alternative implementation,
/// same concept
fn rotate_alt(t: &mut Tetromino) -> () {
    let n = t.area.len();
    let m = t.area[0].len();

    // first rotation
    // with respect to main diagonal
    for i in 0..n {
        for j in i..m {
            let tmp = t.area[i][j];
            t.area[i][j] = t.area[j][i];
            t.area[j][i] = tmp;
        }
    }
    // Second rotation
    // with respect to middle column
    for i in 0..n {
        for j in 0..n/2 {
            let tmp = t.area[i][j];
            t.area[i][j] = t.area[i][n-j-1];
            t.area[i][n-j-1] = tmp;
        }
    }
}

pub trait TetrominoStraight {

    fn make_straight() -> Self;

}

impl TetrominoStraight for Tetromino {

    fn make_straight() -> Tetromino {
        return Tetromino {
            area:
            [[1,0,0,0],
             [1,0,0,0],
             [1,0,0,0],
             [1,0,0,0]],
            name: "straight".to_string(),
            ..Default::default()
        }
    }

}

pub trait TetrominoSquare {
    fn make_square() -> Self;
}

impl TetrominoSquare for Tetromino {
    fn make_square() -> Self {
        return Tetromino {
            area: [[1,1,0,0],
                   [1,1,0,0],
                   [0,0,0,0],
                   [0,0,0,0]],
            name: "square".to_string(),
            ..Default::default()
        }
    }
}

pub trait TetrominoT {
    fn make_t() -> Self;
}

impl TetrominoT for Tetromino {
    fn make_t() -> Self {
        return Tetromino {
            area:
            [[1,1,1,0],
             [0,1,0,0],
             [0,0,0,0],
             [0,0,0,0]],
            name: "t".to_string(),
            ..Default::default()
        }
    }

}

pub trait TetrominoL {
    fn make_l() -> Tetromino;
}

impl TetrominoL for Tetromino {
    fn make_l() -> Tetromino {
        return Tetromino {
            area:
            [[1,0,0,0],
             [1,0,0,0],
             [1,1,0,0],
             [0,0,0,0]],
            name: "l".to_string(),
            ..Default::default()
        }
    }
}

pub trait TetrominoSkew {
    fn make_skew() -> Self;
}

impl TetrominoSkew for Tetromino {
    fn make_skew() -> Self {
        return Tetromino {
            area:
            [[1,1,0,0],
             [0,1,1,0],
             [0,0,0,0],
             [0,0,0,0]],
            name: "skew".to_string(),
            ..Default::default()
        }
    }
}

/// Gets a random tetromino
pub fn get_random_tetromino() -> Tetromino {
    // Get a random in the range [0, 4)
    let num = rand::thread_rng().gen_range(0..4);
    match num {
        0 => return Tetromino::make_straight(),
        1 => return Tetromino::make_l(),
        2 => return Tetromino::make_skew(),
        3 => return Tetromino::make_square(),
        _ => log::error!("Random error generate gave unexpected output."),
    }
    return Tetromino::make_l();
}

#[cfg(test)]
mod tests {
    use crate::tetromino::{TetrominoL, Tetromino};

    #[test]
    fn test_rotate() -> () {
        let mut t = Tetromino::make_l();
        t.area =
            [[1,0,0,0],
             [1,0,0,0],
             [1,1,0,0],
             [1,1,0,0],
        ];
        t.rotate(false);
        let mut expected_result =
            [[1,1,1,1],
             [1,1,0,0],
             [0,0,0,0],
             [0,0,0,0]];
        assert_eq!(t.area, expected_result);
    }

    fn test_rotate_90_basic() {

        let mut t = Tetromino::make_l();
        t.area =
            [
                [1,0,0,0],
                [1,0,0,0],
                [1,1,0,0],
                [1,1,0,0],
            ];
        t.rotate(false);
        let mut expected_result =
            [
                [1,1,1,1],
                [1,1,0,0],
                [0,0,0,0],
                [0,0,0,0],
            ];
        assert_eq!(t.area, expected_result);
    }

    #[test]
    fn test_rotate_90_offset() -> () {
        let mut t = Tetromino::make_l();
        t.x = 0;
        t.y = 0;
        t.rotate(false);
        let mut expected_result =
            [
                [1,1,1,0],
                [1,0,0,0],
                [0,0,0,0],
                [0,0,0,0]
            ];
        assert_eq!(t.area, expected_result);
        t.rotate(false);
        expected_result =
            [
                [1,1,0,0],
                [0,1,0,0],
                [0,1,0,0],
                [0,0,0,0]
            ];
        assert_eq!(t.area, expected_result);
        assert_eq!(t.x, 0);
        assert_eq!(t.y, 0);
        t.rotate(false);
        expected_result =
            [
                [0,0,1,0],
                [1,1,1,0],
                [0,0,0,0],
                [0,0,0,0]
            ];
        assert_eq!(t.area, expected_result);
        assert_eq!(t.x, 0);
        assert_eq!(t.y, 0);
    }

    #[test]
    fn test_rotate_full() -> () {
        let mut t = Tetromino::make_l();
        t.area =
            [[1,2,3,4],
             [5,6,7,8],
             [9,10,11,12],
             [13,14,15,16]];
        t.rotate(false);
        let mut expected_result =
            [[13,9,5,1],
             [14,10,6,2],
             [15,11,7,3],
             [16,12,8,4]];
        assert_eq!(t.area, expected_result);
    }

    #[test]
    fn test_min_max_xy() {
        let mut t = Tetromino::make_l();
        t.x = 0;
        t.y = 0;
        t.area =
            [
                [0, 1, 1, 1],
                [0, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ];

        let (min_x, max_x, min_y, max_y) = t.get_xy_min_max();

        assert_eq!(min_x, 0);
        assert_eq!(min_y, 1);
        assert_eq!(max_x, 1);
        assert_eq!(max_y, 3);
    }

    #[test]
    fn test_min_max_xy_2() {
        let mut t = Tetromino::make_l();
        t.x = 0;
        t.y = 0;
        t.area =
            [
                [0,0,1,0],
                [0,1,1,0],
                [0,1,0,0],
                [0,0,0,0]
            ];
        let (min_x, max_x, min_y, max_y) = t.get_xy_min_max();

        assert_eq!(min_x, 0);
        assert_eq!(min_y, 1);
        assert_eq!(max_x, 2);
        assert_eq!(max_y, 2);
    }
}
