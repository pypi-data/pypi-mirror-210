from src.main.game.Piece import domino_set


def test_domino_set():
    pieces = domino_set()

    assert len(pieces) == 28                # Correct number of pieces
    assert sorted(pieces) == pieces         # Sorted
    assert list(set(pieces)) == pieces      # No duplicate pieces
