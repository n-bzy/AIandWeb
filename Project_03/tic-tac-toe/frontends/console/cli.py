from tic_tac_toe.game.engine import TicTacToe

from .args import parse_args
from .renderers import ConsoleRenderer
from tic_tac_toe.logic.models import GameState, Grid, Mark   # , Move
from tic_tac_toe.logic.exceptions import InvalidMove
# from tic_tac_toe.game.players import Player


class NewTicTacToe(TicTacToe):
    def play(self, inpt, game_state):
        # game_state = GameState(Grid(), starting_mark)
        # grid = self.renderer.render(game_state)
        # print(grid)
        # if game_state.game_over:
        #     return "end"
        player = self.get_current_player(game_state)
        try:
            game_state = player.make_move(inpt, game_state)
        except InvalidMove as ex:
            if self.error_handler:
                self.error_handler(ex)
        return game_state


"""
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
"""


def main(player1, player2, gs, inpt) -> None:
    gs = NewTicTacToe(player1, player2, ConsoleRenderer()).play(inpt, gs)
    return gs


if __name__ == "__main__":
    p1, p2, starting_mark = parse_args()
    starting_mark = Mark("X")
    gs = GameState(Grid(), starting_mark)
    while True:
        grid = ConsoleRenderer().render(game_state=gs)
        print(grid)
        gs = main(p1, p2, gs)
        # print(grid)
        if gs.game_over:
            grid = ConsoleRenderer().render(game_state=gs)
            print(grid)
            if gs.winner:
                print(f"{gs.winner} wins")
            if gs.tie:
                print("No one wins this time")
            break

# TODO:
# Decide on having 1 or 2 grids - 2 is better
# (show every move with a new grid or only every 2nd)
# Update and implement into channel2.py
# Replace every "print()" with the correct function for sending messages
