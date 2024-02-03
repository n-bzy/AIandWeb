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
