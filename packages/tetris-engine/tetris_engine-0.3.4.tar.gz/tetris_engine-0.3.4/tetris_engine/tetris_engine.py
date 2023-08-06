import enum
from typing import List

from tetris_engine_backend import create_game, read_game_multithreaded, write_game_multithreaded, start_game_multithreaded


class Direction(enum.Enum):
    Down = enum.auto()
    Left = enum.auto()
    Right = enum.auto()
    RightRotate = enum.auto()
    LeftRotate = enum.auto()


class Tetromino(enum.Enum):
   Straight = enum.auto() 
   Square = enum.auto()
   T = enum.auto()
   L = enum.auto()
   Skew = enum.auto()


class Tetris:
    """
    A tetris engine powered by rust
    * Supports single threaded operation where the caller controls the game speed
    * Supports multithreading where the engine runs in the background, updating
      the board automatically. The client just supplies the user's commands
    """

    def __init__(self, multithreaded: bool = False):
        """
        Creates a tetris game
        """
        self.multithreaded = multithreaded
        if self.multithreaded:
            self._game = read_game_multithreaded()
            start_game_multithreaded()
        else:
            self._game = create_game()
            self._game.setup_game()

    def restart(self) -> None:
        """
        Creates a new game, overwriting the existing game
        """
        if self.multithreaded:
            raise ValueError("Not yet supported!")
        else:
            self._game = create_game()

    def end_game(self) -> None:
        """
        Ends the current game
        """
        self._game.exit()

    def is_game_running(self) -> bool:
        """
        A check to determine if the current game is still active
        :return: True if the current game is active, False otherwise
        """
        if self.multithreaded:
            self._game = read_game_multithreaded()
        return self._game.is_running()

    def move(self, direction: int = Direction.Down.value) -> None:
        """
        Moves the tetromino
        :param direction: The direction or rotation to apply. Down, left, right, right rotate, and left rotate
        are supported
        """

        if direction == Direction.Left.value:
            self._game.move_left()
        elif direction == Direction.Right.value:
            self._game.move_right()
        elif direction == Direction.Down.value:
            self._game.move_down()
        elif direction == Direction.RightRotate.value:
            self._game.rotate(False)
        elif direction == Direction.LeftRotate.value:
            self._game.rotate(True)
        else:
            raise ValueError("Invalid direction!")

        if self.multithreaded:
            write_game_multithreaded(self._game)

        # does not move the tetromino
        self._game.increment_frame()

    def read_game(self) -> List[List]:
        """
        Get the current state of the game
        """
        if self.multithreaded:
            self._game = read_game_multithreaded()

        return self._game.grid

    def current_tetromino(self) -> Tetromino:
        return self._map_tetromino_name_to_enum(self._game.current_tetromino.name)

    def next_tetromino(self) -> Tetromino:
        return self._map_tetromino_name_to_enum(self._game.next_tetromino.name)

    def _map_tetromino_name_to_enum(self, name: str) -> Tetromino:
        if self._game.current_tetromino.name == "straight":
            return Tetromino.Straight
        elif self._game.current_tetromino.name == "square":
            return Tetromino.Square 
        elif self._game.current_tetromino.name == "t":
            return Tetromino.T
        elif self._game.current_tetromino.name == "l":
            return Tetromino.L
        elif self._game.current_tetromino.name == "skew":
            return Tetromino.Skew
        
    