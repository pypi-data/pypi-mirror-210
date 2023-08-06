from typing import Union, List, Tuple

from src.main.game.Piece import domino_set
from src.main.player import Player


class DominoRound:
    def __init__(self, player1: Player, player2: Player, begins: Union[Player, None]):
        self.pool = domino_set()
        self.source_piece: List[Tuple[int, int]] = []

    def play(self):
        pass