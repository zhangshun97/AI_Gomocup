class role:

    def __init__(self):
        self.empty = 0
        self.AI = 1
        self.opp = 2
        self.mm = 3

    def get_opponent(self, r):
        if not r:
            assert 0, "empty has no opponent"
        if r == self.AI:
            return self.opp
        else:
            return self.AI
