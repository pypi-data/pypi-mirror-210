
from tetris_engine import Tetris, Direction


def test_restart_game():
    tetris = Tetris()
    assert 2 in tetris._game.grid[0]
    tetris.move()
    tetris.restart()
    assert 2 in tetris._game.grid[0]


def test_move_down():
    tetris = Tetris()
    assert 2 in tetris._game.grid[0]
    tetris.move()
    assert 2 not in tetris._game.grid[0]
