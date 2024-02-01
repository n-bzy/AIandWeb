from tic_tac_toe.game.engine import TicTacToe

from args import parse_args
from renderers import ConsoleRenderer
from tic_tac_toe.logic.models import GameState, Grid, Mark
from tic_tac_toe.logic.exceptions import InvalidMove


class NewTicTacToe(TicTacToe):
    def play(self, game_state):
        # game_state = GameState(Grid(), starting_mark)
        self.renderer.render(game_state)
        if game_state.game_over:
            return "end"
        player = self.get_current_player(game_state)
        try:
            game_state = player.make_move(game_state)
        except InvalidMove as ex:
            if self.error_handler:
                self.error_handler(ex)
        return game_state


def main(player1, player2, g) -> None:
    g = NewTicTacToe(player1, player2, ConsoleRenderer()).play(g)
    return g


if __name__ == "__main__":
    p1, p2, starting_mark = parse_args()
    starting_mark = Mark("X")
    g = GameState(Grid(), starting_mark)
    while True:
        g = main(p1, p2, g)
