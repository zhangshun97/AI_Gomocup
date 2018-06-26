from role import role
from negamax import deeping as m
from board import Board
from config import Config

R = role()
config = Config()


class AI:

    def __init__(self, board):
        self.theBoard = Board(board)
        self.turnChecked = False  # 用来对应非空开局，确定先后手

    def get_move(self):
        p = self.theBoard.maxmin(config.searchDeep)
        return p

    def set(self, move, player):
        self.theBoard.put(move, player, True)

    def back(self):
        self.theBoard.back()

    def get_opponent_move(self, board):
        for x in range(self.theBoard.height):  # |
            for y in range(self.theBoard.width):  # \
                if self.theBoard.board[x][y] != board[x][y]:
                    # which means the opponent takes move (x, y)
                    return x, y
        return 0
