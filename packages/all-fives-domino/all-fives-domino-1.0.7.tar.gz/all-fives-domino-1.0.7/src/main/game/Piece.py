from typing import List, Union


class Piece:
    def __init__(self, a: int, b: int):
        """
        Constructor

        a: int                  -> First number on the piece
        b: int                  -> Second number on the piece

        linked: List[Piece]     -> Pieces played from this Piece
        is_crossing: Bool       -> Whether Pieces can be appended to all four sides of this Piece
        is_double: Bool         -> Whether both sides of the piece show the same number
        closed: Bool            -> If a double piece is closed (face down), nothing can be appended to it
        points: int             -> Point value of the piece, which is the combined value of both sides
        """
        if a < 0 or b < 0 or a > 6 or b > 6:
            raise ValueError(f"Domino Piece sides can only have values 0-6, got [{a}|{b}]")

        self.sides = sorted([a, b])
        self.linked: List[Piece] = []
        self.linked_to: Union[Piece, None] = None
        self.is_crossing = False
        self.is_double = self.sides[0] == self.sides[1]
        self.closed = False
        self.points = sum(self.sides)

    def append(self, piece):
        self.linked.append(piece)

    def unlinked_side(self, other: "Piece") -> int:
        a, b = self.sides
        return b if a in other.sides else a

    def __str__(self):
        """Simple visual representation using die face Unicode symbols"""
        if self.closed:
            closed = u"\u25A9"
            return f"[{closed}|{closed}]"

        sides = [
            u"\u25A1",
            u"\u2680",
            u"\u2681",
            u"\u2682",
            u"\u2683",
            u"\u2684",
            u"\u2685"
        ]

        return f"[{sides[self.sides[0]]}|{sides[self.sides[1]]}]"

    def __repr__(self):
        """Use string representation"""
        return str(self)

    def __hash__(self):
        """Integer representation, e.g. 46 for a [4|6] piece"""
        return self.sides[0] * 10 + self.sides[1]

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
