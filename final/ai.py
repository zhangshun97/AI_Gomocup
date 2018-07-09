from role import role
import numpy as np
from boardHHH import Board
from config import Config
from vcx import vcf, vct


R = role()
config = Config()


class AI:

    def __init__(self, board):
        self.theBoard = Board(board)
        self.turnChecked = False  # 用来对应非空开局，确定先后手
        self.start = True
        self.searchDeep = config.searchDeep_white
        self.searchDeep_ = config.searchDeep_white
        self.if_found_vcx = False

    def get_move(self):
        if self.start:
            self.start = False
            if np.sum(self.theBoard.board):
                pass
            else:
                return (self.theBoard.size // 2, self.theBoard.size // 2), 1

        p, if_only = self.theBoard.negamax(self.searchDeep, config.spreadLimit)
        return p, if_only

    def get_move_vcx(self):
        if self.start:
            self.start = False
            if np.sum(self.theBoard.board):
                pass
            else:
                return self.theBoard.size // 2, self.theBoard.size // 2
        # for deep in range(1, config.vcxDeep):
        p = vcf(self.theBoard, R.AI, config.vcxDeep)
        if p:
            return p
        else:
            return vct(self.theBoard, R.AI, config.vcxDeep)

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

    def white_or_black(self):
        c = 0
        for x in range(self.theBoard.height):  # |
            for y in range(self.theBoard.width):  # \
                if self.theBoard.board[x][y] != R.empty:
                    c += 1
        return (c + 1) % 2  # True for black
