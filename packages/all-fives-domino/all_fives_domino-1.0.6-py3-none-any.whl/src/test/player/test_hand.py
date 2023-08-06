from src.main.player.Hand import Hand, Piece


def test_hand_sorting():
    hand = Hand(Piece(3, 3), Piece(0, 1))
    assert hand.pieces == [Piece(0, 1), Piece(3, 3)]
    hand.add(Piece(2, 2))
    assert hand.pieces == [Piece(0, 1), Piece(2, 2), Piece(3, 3)]

