from tetris_engine import Tetris, Direction, Tetromino


def test_rust_lib():
    """
    Tests the underlying rust library
    """
    t = Tetris()._game
    t.setup_game()
    while t.is_running():
        t.move_down()
        t.increment_frame()

    assert True


def test_singlethreaded():
    """
    Tests a simple running of the game
    """
    tetris = Tetris()
    while tetris.is_game_running():
        tetris.move(direction=Direction.Down.value)
    assert True


def test_multithreaded():
    """
    Tests that the underlying game grid changes when 
    running in multithreaded mode
    """
    tetris = Tetris(multithreaded=True)
    old_grid = tetris._game.grid
    test_passes = False
    while tetris.is_game_running():
        tetris.read_game()
        new_grid = tetris._game.grid
        if old_grid != new_grid:
            test_passes = True
            for row in old_grid:
                print(row)
            print()

            for row in new_grid:
                print(row)
            print()
            break
    assert test_passes

def test_next_tetromino():
    tetris = Tetris()
    current_tetromino = tetris.current_tetromino()
    assert isinstance(current_tetromino, Tetromino)
    next_tetromino = tetris.next_tetromino()
    assert isinstance(next_tetromino, Tetromino)