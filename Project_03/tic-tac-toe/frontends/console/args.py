import argparse
from typing import NamedTuple
import re
import abc
import time

from tic_tac_toe.game.players import (
    Player,
    RandomComputerPlayer,
    # MinimaxComputerPlayer,
)
from tic_tac_toe.logic.models import Mark, GameState, Move
from tic_tac_toe.logic.exceptions import InvalidMove
from tic_tac_toe.logic.minimax import find_best_move

# from players import ConsolePlayer
# from .cli import NewConsolePlayer


class NewConsolePlayer(Player):
    def get_move(self, inpt, game_state: GameState) -> Move | None:
        while not game_state.game_over:
            try:
                # index = grid_to_index(input(f"{self.mark}'s move: ").strip())
                index = grid_to_index(inpt.strip())
            except ValueError:
                print("Please provide coordinates in the form of A1 or 1A")
            else:
                try:
                    return game_state.make_move_to(index)
                except InvalidMove:
                    print("That cell is already occupied.")
        return None

    def make_move(self, inpt, game_state: GameState) -> GameState:
        if self.mark is game_state.current_mark:
            if move := self.get_move(inpt, game_state):
                return move.after_state
            raise InvalidMove("No more possible moves")
        else:
            raise InvalidMove("It's the other player's turn")


def grid_to_index(grid: str) -> int:
    if re.match(r"[abcABC][123]", grid):
        col, row = grid
    elif re.match(r"[123][abcABC]", grid):
        row, col = grid
    else:
        raise ValueError("Invalid grid coordinates")
    return 3 * (int(row) - 1) + (ord(col.upper()) - ord("A"))


class NewComputerPlayer(Player, metaclass=abc.ABCMeta):
    def __init__(self, mark: Mark, delay_seconds: float = 0.25) -> None:
        super().__init__(mark)
        self.delay_seconds = delay_seconds

    def get_move(self, game_state: GameState) -> Move | None:
        time.sleep(self.delay_seconds)
        return self.get_computer_move(game_state)

    def make_move(self, inpt, game_state: GameState) -> GameState:
        if self.mark is game_state.current_mark:
            if move := self.get_move(game_state):
                return move.after_state
            raise InvalidMove("No more possible moves")
        else:
            raise InvalidMove("It's the other player's turn")

    @abc.abstractmethod
    def get_computer_move(self, game_state: GameState) -> Move | None:
        """Return the computer's move in the given game state."""


class NewMinimaxComputerPlayer(NewComputerPlayer):
    def get_computer_move(self, game_state: GameState) -> Move | None:
        if game_state.game_not_started:
            return game_state.make_random_move()
        else:
            return find_best_move(game_state)


PLAYER_CLASSES = {
    "human": NewConsolePlayer,
    "random": RandomComputerPlayer,
    "minimax": NewMinimaxComputerPlayer,
}


class Args(NamedTuple):
    player1: Player
    player2: Player
    starting_mark: Mark


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-X",
        dest="player_x",
        choices=PLAYER_CLASSES.keys(),
        default="human",
    )
    parser.add_argument(
        "-O",
        dest="player_o",
        choices=PLAYER_CLASSES.keys(),
        default="minimax",
    )
    parser.add_argument(
        "--starting",
        dest="starting_mark",
        choices=Mark,
        type=Mark,
        default="X",
    )
    args = parser.parse_args()

    player1 = PLAYER_CLASSES[args.player_x](Mark("X"))
    player2 = PLAYER_CLASSES[args.player_o](Mark("O"))

    if args.starting_mark == "O":
        player1, player2 = player2, player1

    return Args(player1, player2, args.starting_mark)
