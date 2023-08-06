from typing import List, Tuple

from src.main.game.Piece import Piece


class Hand:
    def __init__(self, *pieces: Piece):
        self.pieces: List[Piece] = list(pieces)
        self.order()

    def add(self, piece: Piece):
        self.pieces.append(piece)
        self.order()

    def pop(self, piece: Piece):
        self.pieces = [p for p in self.pieces if p != piece]
        self.order()
        return piece

    def order(self):
        self.pieces.sort()

    def __iter__(self):
        for piece in self.pieces:
            yield piece
