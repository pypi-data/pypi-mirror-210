from src.main.player.Hand import Hand, Piece


def test_hand_add_pop_sorting():
    hand = Hand(Piece(3, 3), Piece(0, 1))
    assert hand.pieces == [Piece(0, 1), Piece(3, 3)]
    hand.add(Piece(2, 2))
    assert hand.pieces == [Piece(0, 1), Piece(2, 2), Piece(3, 3)]
    hand.pop(Piece(3, 3))
    assert hand.pieces == [Piece(0, 1), Piece(2, 2)]


def test_in_hand():
    hand = Hand(Piece(3, 3), Piece(0, 1))
    assert Piece(3, 3) in hand
    assert Piece(0, 1) in hand
    assert Piece(1, 0) in hand

    assert Piece(2, 1) not in hand
    assert Piece(5, 5) not in hand
