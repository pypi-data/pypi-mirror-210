import pytest

from src.main.game.Piece import domino_set, Piece


def test_domino_set():
    pieces = domino_set()

    assert len(pieces) == 28                        # Correct number of pieces
    assert sorted(pieces) == pieces                 # Sorted
    assert sorted(list(set(pieces))) == pieces      # No duplicate pieces


def test_no_invalid_pieces():
    for a, b in [(-1, -1), (-1, 3), (-7, 0), (2, 8), (8, 100)]:
        with pytest.raises(ValueError):
            Piece(a, b)


def test_piece_value():
    assert Piece(3, 4).points == 7
    assert Piece(3, 3).points == 6
    assert Piece(0, 0).points == 0


def test_piece_sorting():
    assert sorted([Piece(3, 4), Piece(0, 1), Piece(4, 4)]) == [Piece(0, 1), Piece(3, 4), Piece(4, 4)]


def test_piece_equality():
    assert Piece(3, 4) == Piece(3, 4)
    assert Piece(1, 2) != Piece(0, 3)


def test_piece_comparison():
    assert Piece(1, 2) < Piece(3, 4)
    assert Piece(0, 6) > Piece(4, 1)


def test_piece_hashing():
    assert hash(Piece(4, 3)) == 34
    assert hash(Piece(0, 0)) == 0
    assert hash(Piece(6, 6)) == 66
    assert hash(Piece(6, 4)) == 46


def test_piece_stringification():
    assert str(Piece(2, 3)) == '[⚁|⚂]'


def test_unlinked_side_detection():
    assert Piece(2, 3).unlinked_side(Piece(3, 3)) == 2
    assert Piece(3, 3).unlinked_side(Piece(3, 6)) == 3
    assert Piece(4, 5).unlinked_side(Piece(0, 4)) == 5
