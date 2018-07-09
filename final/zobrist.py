from role import role
import numpy as np

R = role()


class Zobrist:

    def __init__(self, size):
        self.size = size

    def init(self):
        self.AIHashing = np.random.randint(9223372036854775807, size=(20, 20), dtype='int64')
        self.oppHashing = np.random.randint(9223372036854775807, size=(20, 20), dtype='int64')
        self.boardHashing = np.random.randint(9223372036854775807, size=1, dtype='int64')

    def go(self, position, player):
        if player == R.AI:
            self.boardHashing ^= self.AIHashing[position]
        elif player == R.opp:
            self.boardHashing ^= self.oppHashing[position]
        else:
            assert 0, "empty do not take hashing move"
