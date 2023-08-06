from typing import Union, List, Tuple

from src.main.game.Piece import domino_set
from src.main.player.Player import Player
from src.main.player.Brain import Brain
from src.main.player.Hand import Hand


class DominoRound:
    def __init__(self, player1: Player, player2: Player, begins: Union[Player, None]):
        self.pool = domino_set()
        self.source_piece: List[Tuple[int, int]] = []
        self.player1 = player1
        self.player2 = player2
        self.current_player = begins

    def deal_hand(self):
        # Each player receives 7 pieces
        for i in range(7):
            self.player1.draw()
            self.player2.draw()

    def neutral_start(self):
        """
        If no starting player is defined, the player with [5|5] begins.

        If neither player has [5|5], the order goes [1|1], [2|2], ..., [6|6], [0|0].
        If neither player has any double pieces, they draw a piece each until one does.
        """
        while self.current_player is None:
            pass

    def valid_options(self, hand):
        return []

    def play(self):
        while True:
            self.current_player.play()
