from src.main.game.DominoRound import DominoRound
from src.main.player.Hand import Hand
from src.main.player.Brain import Brain


class Player:
    def __init__(self, brain: Brain, round: DominoRound):
        self.hand = Hand()
        self.score = 0
        self.brain = brain
        self.round = round

    def play(self):
        return self.brain.play(self, self.round)

    def draw(self):
        piece = self.round.pool.pop()
        self.hand.add(piece)
