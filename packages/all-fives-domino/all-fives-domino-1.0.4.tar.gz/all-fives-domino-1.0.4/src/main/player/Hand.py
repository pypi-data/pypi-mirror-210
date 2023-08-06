from typing import List, Union

from src.main.game.Piece import Piece


class Hand:
    def __init__(self, pieces: Union[List[Piece], None] = None):
        self.pieces: List[Piece] = [] if pieces is None else pieces

    def add(self, piece: Piece):
        self.pieces.append(piece)