import random
import copy
import math as np
import time

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

# the full-rule based table
# here always assume AI is 1, the opponent is 2 and vacancy is 0
get_points = {
    # ------ 1 ------
    '00000': (1, 1, 1, 1, 1),
    '00001': (1, 2, 2, 2, 0),
    '00010': (2, 2, 2, 0, 2),
    '00011': (3, 4, 4, 0, 0),
    '00100': (2, 2, 0, 2, 2),
    '00101': (3, 4, 0, 4, 0),
    '00110': (4, 4, 0, 0, 4),
    '00111': (6, 7, 0, 0, 0),
    '01000': (2, 0, 2, 2, 2),
    '01001': (3, 0, 4, 4, 0),
    '01010': (4, 0, 4, 0, 4),
    '01011': (5, 0, 7, 0, 0),
    '01100': (4, 0, 0, 4, 4),
    '01101': (6, 0, 0, 7, 0),
    '01110': (7, 0, 0, 0, 7),
    '01111': (8, 0, 0, 0, 0),
    '10000': (0, 2, 2, 2, 1),
    '10001': (0, 3, 3, 3, 0),
    '10010': (0, 4, 4, 0, 3),
    '10011': (0, 5, 6, 0, 0),
    '10100': (0, 4, 0, 4, 3),
    '10101': (0, 6, 0, 6, 0),
    '10110': (0, 7, 0, 0, 6),
    '10111': (0, 8, 0, 0, 0),
    '11000': (0, 0, 4, 4, 3),
    '11001': (0, 0, 6, 5, 0),
    '11010': (0, 0, 7, 0, 5),
    '11011': (0, 0, 8, 0, 0),
    '11100': (0, 0, 0, 7, 6),
    '11101': (0, 0, 0, 8, 0),
    '11110': (0, 0, 0, 0, 8),
    '11111': (0, 0, 0, 0, 0),
    # ------ 2 -------
    '000002': (1, 1, 1, 1, 0),
    '000012': (1, 1, 1, 1, 0),
    '000102': (2, 2, 2, 0, 1),
    '000112': (3, 3, 3, 0, 0),
    '001002': (2, 2, 0, 2, 1),
    '001012': (3, 3, 0, 3, 0),
    '001102': (4, 4, 0, 0, 3),
    '001112': (5, 5, 0, 0, 0),
    '010002': (2, 0, 2, 2, 1),
    '010012': (3, 0, 3, 3, 0),
    '010102': (4, 0, 4, 0, 3),
    '010112': (5, 0, 5, 0, 0),
    '011002': (4, 0, 0, 4, 3),
    '011012': (6, 0, 0, 5, 0),
    '011102': (7, 0, 0, 0, 5),
    '011112': (8, 0, 0, 0, 0),
    '100002': (0, 2, 2, 2, 1),
    '100012': (0, 3, 3, 3, 0),
    '100102': (0, 4, 4, 0, 3),
    '100112': (0, 5, 5, 0, 0),
    '101002': (0, 4, 0, 4, 3),
    '101012': (0, 6, 0, 5, 0),
    '101102': (0, 7, 0, 0, 5),
    '101112': (0, 8, 0, 0, 0),
    '110002': (0, 0, 4, 4, 3),
    '110012': (0, 0, 6, 5, 0),
    '110102': (0, 0, 7, 0, 5),
    '110112': (0, 0, 8, 0, 0),
    '111002': (0, 0, 0, 7, 6),
    '111012': (0, 0, 0, 8, 0),
    '111102': (0, 0, 0, 0, 8),
    '111112': (0, 0, 0, 0, 0),
    # ------ 3 -------
    '200000': (1, 1, 1, 1, 1),
    '200001': (0, 3, 3, 3, 0),
    '200010': (0, 3, 3, 0, 3),
    '200011': (0, 5, 6, 0, 0),
    '200100': (0, 3, 0, 3, 3),
    '200101': (0, 5, 0, 6, 0),
    '200110': (0, 5, 0, 0, 6),
    '200111': (0, 8, 0, 0, 0),
    '201000': (1, 0, 2, 2, 2),
    '201001': (3, 0, 4, 4, 0),
    '201010': (3, 0, 4, 0, 4),
    '201011': (5, 0, 7, 0, 0),
    '201100': (3, 0, 0, 4, 4),
    '201101': (5, 0, 0, 7, 0),
    '201110': (5, 0, 0, 0, 7),
    '201111': (8, 0, 0, 0, 0),
    '210000': (1, 1, 1, 1, 1),
    '210001': (0, 3, 3, 3, 0),
    '210010': (0, 3, 3, 0, 3),
    '210011': (0, 5, 6, 0, 0),
    '210100': (0, 3, 0, 3, 3),
    '210101': (0, 5, 0, 6, 0),
    '210110': (0, 5, 0, 0, 6),
    '210111': (0, 8, 0, 0, 0),
    '211000': (0, 0, 3, 3, 3),
    '211001': (0, 0, 5, 5, 0),
    '211010': (0, 0, 5, 0, 5),
    '211011': (0, 0, 8, 0, 0),
    '211100': (0, 0, 0, 5, 5),
    '211101': (0, 0, 0, 8, 0),
    '211110': (0, 0, 0, 0, 8),
    '211111': (0, 0, 0, 0, 0),
    # ------ 4 -------
    '2000002': (0, 0, 0, 0, 0),
    '2000012': (1, 1, 1, 1, 0),
    '2000102': (1, 1, 1, 0, 1),
    '2000112': (3, 3, 3, 0, 0),
    '2001002': (1, 1, 0, 1, 1),
    '2001012': (3, 3, 0, 3, 0),
    '2001102': (3, 3, 0, 0, 3),
    '2001112': (5, 5, 0, 0, 0),
    '2010002': (1, 0, 1, 1, 1),
    '2010012': (3, 0, 3, 3, 0),
    '2010102': (3, 0, 3, 0, 3),
    '2010112': (5, 0, 5, 0, 0),
    '2011002': (3, 0, 0, 3, 3),
    '2011012': (5, 0, 0, 5, 0),
    '2011102': (5, 0, 0, 0, 5),
    '2011112': (8, 0, 0, 0, 0),
    '2100002': (0, 1, 1, 1, 1),
    '2100012': (0, 3, 3, 3, 0),
    '2100102': (0, 3, 3, 0, 3),
    '2100112': (0, 5, 5, 0, 0),
    '2101002': (0, 3, 0, 3, 3),
    '2101012': (0, 5, 0, 5, 0),
    '2101102': (0, 5, 0, 0, 5),
    '2101112': (0, 8, 0, 0, 0),
    '2110002': (0, 0, 3, 3, 3),
    '2110012': (0, 0, 5, 5, 0),
    '2110102': (0, 0, 5, 0, 5),
    '2110112': (0, 0, 8, 0, 0),
    '2111002': (0, 0, 0, 5, 5),
    '2111012': (0, 0, 0, 8, 0),
    '2111102': (0, 0, 0, 0, 8),
    '2111112': (0, 0, 0, 0, 0),
}


class PointBoard:

    def __init__(self, input_board):
        self.height = len(input_board)
        self.width = len(input_board[0])
        self.board = copy.deepcopy(input_board)
        self.values = copy.deepcopy(input_board)
        self.n_in_line = 5  # default as standard Gomoku
        # get the initial value
        for x in range(self.height):  # |
            for y in range(self.width):  # \
                self.get_value(player=self.board[x][y], move=(x, y))

    def get_value(self, player, move):
        # TODO: get the initial values
        if player == 0:
            self.values[move[0]][move[1]] = max(self.values[move[0]][move[1]], 1)
        else:
            self.dynamic_scan(player, move)

    def get_opponent(self):
        for x in range(self.height):  # |
            for y in range(self.width):  # \
                if self.board[x][y] != board[x][y]:
                    # which means the opponent takes move (x, y)
                    return x, y
        return 0

    def update_values(self, moves, values):
        """
        update the values based on taking maximum.
        :param moves: a list of moves
        :param values: a tuple of values
        :return: nothing
        """
        assert len(moves) > 0, "no move to update"
        assert len(values) == len(moves), "move-value pairs not coherent"
        for i in range(len(moves)):
            self.values[moves[i][0]][moves[i][1]] = max(self.values[moves[i][0]][moves[i][1]], values[i])

    def dynamic_scan(self, player, move):
        # update the board
        x_this, y_this = move
        self.board[x_this][y_this] = player

        # get the boundaries
        up = min(x_this, self.n_in_line - 1)
        down = min(self.height - 1 - x_this, self.n_in_line - 1)
        left = min(y_this, self.n_in_line - 1)
        right = min(self.width - 1 - y_this, self.n_in_line - 1)
        # \
        up_left = min(up, left)
        down_right = min(down, right)
        for i in range(up_left + down_right - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this - up_left + i - 1, y_this - up_left + i - 1
            if head[0] < 0 or head[1] < 0:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == 2:
                key += '2'

            for j in range(self.n_in_line):
                key += str(self.board[x_this - up_left + i + j][y_this - up_left + i + j])
                moves.append((x_this - up_left + i + j, y_this - up_left + i + j))

            tail = x_this - up_left + i + 5, y_this - up_left + i + 5
            if tail[0] >= self.height or tail[1] >= self.width:  # hit the wall
                key += '2'
            elif self.board[tail[0]][tail[1]] == 2:
                key += '2'
            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)))

        # /
        up_right = min(up, right)
        down_left = min(down, left)
        for i in range(up_right + down_left - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this - up_right + i - 1, y_this + up_right - i + 1
            if head[0] < 0 or head[1] >= self.width:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == 2:
                key += '2'

            for j in range(self.n_in_line):
                key += str(self.board[x_this - up_right + i + j][y_this + up_right - i - j])
                moves.append((x_this - up_right + i + j, y_this + up_right - i - j))

            tail = x_this - up_right + i + 5, y_this + up_right - i - 5
            if tail[0] >= self.height or tail[1] < 0:  # hit the wall
                key += '2'
            elif self.board[tail[0]][tail[1]] == 2:
                key += '2'
            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)))

        # --
        for i in range(left + right - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this, y_this - left + i - 1
            if head[1] < 0:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == 2:
                key += '2'

            for j in range(self.n_in_line):
                key += str(self.board[x_this][y_this - left + i + j])
                moves.append((x_this, y_this - left + i + j))

            tail = x_this, y_this - left + i + 5
            if tail[1] >= self.width:
                key += '2'
            elif self.board[tail[0]][tail[1]] == 2:
                key += '2'

            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)))

        # |
        for i in range(up + down - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this - up + i - 1, y_this
            if head[0] < 0:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == 2:
                key += '2'

            for j in range(self.n_in_line):
                key += str(self.board[x_this - up + i + j][y_this])
                moves.append((x_this - up + i + j, y_this))

            tail = x_this - up + i + 5, y_this
            if tail[0] >= self.height:
                key += '2'
            elif self.board[tail[0]][tail[1]] == 2:
                key += '2'

            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)))
