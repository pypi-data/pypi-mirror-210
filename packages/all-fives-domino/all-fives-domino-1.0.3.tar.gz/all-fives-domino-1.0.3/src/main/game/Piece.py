from typing import List


class Piece:
    def __init__(self, a: int, b: int):
        """
        Constructor

        a: int                  -> First number on the piece
        b: int                  -> Second number on the piece

        linked: List[Piece]     -> Pieces played from this Piece
        is_crossing: Bool       -> Whether Pieces can be appended to all four sides of this Piece
        """
        self.sides = sorted([a, b])
        self.linked: List[Piece] = []
        self.is_crossing = False

    def append(self, piece):
        self.linked.append(piece)

    @property
    def points(self):
        """Returns the point value of the piece, which is the combined value of both sides"""
        return sum(self.sides)

    def __repr__(self):
        """Simple visual representation, e.g. [4|6]"""
        return f"[{self.sides[0]}|{self.sides[1]}]"

    def __hash__(self):
        """Integer representation, e.g. 64 for a [4|6] piece"""
        return self.sides[1] * 10 + self.sides[0]

    def __eq__(self, other):
        """Returns whether the pieces are equal based on their hash"""
        return hash(self) == hash(other)

    def __lt__(self, other):
        """Returns whether a piece is bigger based on point value"""
        return self.points < other.points

    def __gt__(self, other):
        """Returns whether a piece is smaller based on point value"""
        return self.points > other.points


def domino_set():
    pieces = set()
    for i in range(7):
        for j in range(7):
            if i <= j:
                pieces.add(Piece(i, j))
    return sorted(pieces)


if __name__ == '__main__':
    print(domino_set())
