import random
import copy
import math as np
import time

MAX_BOARD = 10
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

Point_Board = None


class PointBoard:

    def __init__(self, input_board, players=(1, 2)):
        self.height = len(input_board)
        self.width = len(input_board[0])
        self.board = copy.deepcopy(input_board)
        self.my_player = players[0]
        self.opponent_player = players[1]
        self.get_opponent = {
            players[0]: players[1],
            players[1]: players[0],
        }
        self.if_board_not_empty = None
        self.values = copy.deepcopy(input_board)            # for attack
        self.opponent_values = copy.deepcopy(input_board)   # for defence
        self.n_in_line = 5  # default as standard Gomoku
        # get the initial values for me
        for x in range(self.height):  # |
            for y in range(self.width):  # \
                self.get_value(player=self.board[x][y], move=(x, y))
        # get the initial values for opponent
        for x in range(self.height):  # |
            for y in range(self.width):  # \
                self.get_value(player=self.board[x][y], move=(x, y))

    def get_value(self, player, move):
        if player == 0:
            self.values[move[0]][move[1]] = max(self.values[move[0]][move[1]], 0)
            self.opponent_values[move[0]][move[1]] = max(self.opponent_values[move[0]][move[1]], 0)
        else:
            # TODO: check if this is right for a given non-empty board
            self.dynamic_update(player, move)

    def get_move(self):
        if self.if_board_not_empty is None:
            self.if_board_not_empty = sum(
                sum(row) for row in self.board
            )
        if self.if_board_not_empty:
            point, move = max(
                (Point_Board.values[i][j], (i, j))
                for i in range(Point_Board.height)
                for j in range(Point_Board.width)
            )
            point_opponent, move_opponent = max(
                (Point_Board.opponent_values[i][j], (i, j))
                for i in range(Point_Board.height)
                for j in range(Point_Board.width)
            )
            if point_opponent > point:
                return point_opponent, move_opponent
        else:
            point, move = 0, (self.height // 2, self.width // 2)
            self.if_board_not_empty = 1

        return point, move

    def get_opponent_move(self):
        for x in range(self.height):  # |
            for y in range(self.width):  # \
                if self.board[x][y] != board[x][y]:
                    # which means the opponent takes move (x, y)
                    return x, y
        return 0

    def update_values(self, moves, values, player):
        """
        update the values based on taking maximum.
        :param moves: a list of moves
        :param values: a tuple of values
        :param player: determine which value-set to update
        """
        assert len(moves) > 0, "no move to update"
        assert len(values) == len(moves), "move-value pairs not coherent"
        if player == self.my_player:
            for i in range(len(moves)):
                self.values[moves[i][0]][moves[i][1]] = max(self.values[moves[i][0]][moves[i][1]], values[i])
        elif player == self.opponent_player:
            for i in range(len(moves)):
                self.opponent_values[moves[i][0]][moves[i][1]] = max(self.opponent_values[moves[i][0]][moves[i][1]],
                                                                     values[i])
        else:
            raise Exception("player setting error")

    def dynamic_update(self, player, move):
        # update the board
        x_this, y_this = move
        self.board[x_this][y_this] = player
        """
        Note:
            Here '2' means the opponent of input 'player', and we consider the wall as '2' too,
            so a pattern '2110012' could mean 'OXX--XO' or 'XOO--OX' in actual board.
            By doing so, we can update both my-value-set and opponent-value-set through one function.
        """
        # get the boundaries
        up = min(x_this, self.n_in_line - 1)
        down = min(self.height - 1 - x_this, self.n_in_line - 1)
        left = min(y_this, self.n_in_line - 1)
        right = min(self.width - 1 - y_this, self.n_in_line - 1)
        # \
        up_left = min(up, left)
        down_right = min(down, right)
        # first set to 0
        # TODO: set to 0 should be modified
        if player == self.my_player:
            for i in range(up_left + down_right + 1):
                self.values[x_this - up_left + i][y_this - up_left + i] = 0
        else:
            for i in range(up_left + down_right + 1):
                self.values[x_this - up_left + i][y_this - up_left + i] = 0

        # then update
        for i in range(up_left + down_right - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this - up_left + i - 1, y_this - up_left + i - 1
            if head[0] < 0 or head[1] < 0:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == self.get_opponent[player]:
                key += '2'

            for j in range(self.n_in_line):
                if self.board[x_this - up_left + i + j][y_this - up_left + i + j] == player:
                    key += '1'
                elif self.board[x_this - up_left + i + j][y_this - up_left + i + j] == self.get_opponent[player]:
                    key += '2'
                else:
                    key += '0'
                moves.append((x_this - up_left + i + j, y_this - up_left + i + j))

            tail = x_this - up_left + i + 5, y_this - up_left + i + 5
            if tail[0] >= self.height or tail[1] >= self.width:  # hit the wall
                key += '2'
            elif self.board[tail[0]][tail[1]] == self.get_opponent[player]:
                key += '2'
            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)), player)

        # /
        up_right = min(up, right)
        down_left = min(down, left)
        # first set to 0
        for i in range(up_right + down_left + 1):
            self.values[x_this - up_right + i][y_this + up_right - i] = 0

        # then update
        for i in range(up_right + down_left - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this - up_right + i - 1, y_this + up_right - i + 1
            if head[0] < 0 or head[1] >= self.width:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == self.get_opponent[player]:
                key += '2'

            for j in range(self.n_in_line):
                if self.board[x_this - up_right + i + j][y_this + up_right - i - j] == player:
                    key += '1'
                elif self.board[x_this - up_right + i + j][y_this + up_right - i - j] == self.get_opponent[player]:
                    key += '2'
                else:
                    key += '0'
                moves.append((x_this - up_right + i + j, y_this + up_right - i - j))

            tail = x_this - up_right + i + 5, y_this + up_right - i - 5
            if tail[0] >= self.height or tail[1] < 0:  # hit the wall
                key += '2'
            elif self.board[tail[0]][tail[1]] == self.get_opponent[player]:
                key += '2'
            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)), player)

        # --
        # first set to 0
        for i in range(left + right + 1):
            self.values[x_this][y_this - left + i] = 0

        # then update
        for i in range(left + right - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this, y_this - left + i - 1
            if head[1] < 0:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == self.get_opponent[player]:
                key += '2'

            for j in range(self.n_in_line):
                if self.board[x_this][y_this - left + i + j] == player:
                    key += '1'
                elif self.board[x_this][y_this - left + i + j] == self.get_opponent[player]:
                    key += '2'
                else:
                    key += '0'
                moves.append((x_this, y_this - left + i + j))

            tail = x_this, y_this - left + i + 5
            if tail[1] >= self.width:
                key += '2'
            elif self.board[tail[0]][tail[1]] == self.get_opponent[player]:
                key += '2'

            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)), player)

        # |
        # first set to 0
        for i in range(up + down + 1):
            self.values[x_this - up + i][y_this] = 0

        # then update
        for i in range(up + down - self.n_in_line + 2):
            key = ''
            moves = []
            head = x_this - up + i - 1, y_this
            if head[0] < 0:  # hit the wall
                key += '2'
            elif self.board[head[0]][head[1]] == self.get_opponent[player]:
                key += '2'

            for j in range(self.n_in_line):
                if self.board[x_this - up + i + j][y_this] == player:
                    key += '1'
                elif self.board[x_this - up + i + j][y_this] == self.get_opponent[player]:
                    key += '2'
                else:
                    key += '0'
                moves.append((x_this - up + i + j, y_this))

            tail = x_this - up + i + 5, y_this
            if tail[0] >= self.height:
                key += '2'
            elif self.board[tail[0]][tail[1]] == self.get_opponent[player]:
                key += '2'

            assert len(key) <= self.n_in_line + 2, "error when update values on board"

            # update_values based on MAXIMUM
            self.update_values(moves, get_points.get(key, (0, 0, 0, 0, 0)), player)


class PP:
    # zs: to simulate the pisqpipe package
    def __init__(self):
        self.height = MAX_BOARD
        self.width = MAX_BOARD
        self.terminateAI = None

    def pipeOut(self, what):
        print(what)

    def do_mymove(self, x, y):
        brain_my(x, y)
        self.pipeOut("{},{}".format(x, y))

    def do_oppmove(self, x, y):
        brain_opponents(x, y)
        self.pipeOut("{},{}".format(x, y))


def brain_turn():
    """
    MCTS
    Useful materials:
        class:
            Board
            MCTS
    """
    if pp.terminateAI:
        return

    global Point_Board
    opp_move = Point_Board.get_opponent_move()
    Point_Board.dynamic_update(2, opp_move)

    i = 0
    while True:
        point, move = Point_Board.get_move()
        x, y = move

        Point_Board.dynamic_update(1, move)
        for row in Point_Board.values:
            print(row)
        print('=-'*20)
        for row in Point_Board.opponent_values:
            print(row)
        break  # TODO: here is a bug
        if pp.terminateAI:
            return

        if isFree(x, y):
            break
    if i > 1:
        # zs: maybe useful to debug
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    pp.do_mymove(x, y)


def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return

    global Point_Board
    Point_Board = PointBoard(board)

    pp.pipeOut("OK")


def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0

    global Point_Board
    Point_Board = PointBoard(board)

    pp.pipeOut("OK")


def isFree(x, y):
    """whether (x, y) is available"""
    return 0 <= x < pp.width and 0 <= y < pp.height and board[x][y] == 0


def brain_my(x, y):
    """my turn: take the step on (x,y)"""
    if isFree(x, y):
        board[x][y] = 1
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    """oppoent's turn: take the step on (x,y)"""
    if isFree(x, y):
        board[x][y] = 2
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_block(x, y):
    """???"""
    if isFree(x, y):
        board[x][y] = 3
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))


def brain_takeback(x, y):
    """take back the chess on (x,y)"""
    if 0 <= x < pp.width and 0 <= y < pp.height and board[x][y] != 0:
        board[x][y] = 0
        return 0
    return 2


def brain_end(x, y):
    pass


def brain_about():
    pp.pipeOut(pp.infotext)


def brain_show():
    st = '  '
    for i in range(len(board[0])):
        if i > 9:
            st += str(i) + ' '
        else:
            st += ' ' + str(i) + ' '
    print(st)
    c = 0
    for row in board:
        if c > 9:
            print(c, end=' ')
        else:
            print('', c, end=' ')
        c += 1
        st = ''
        for ii in row:
            if ii == 1:
                st += 'O  '
            elif ii == 2:
                st += 'X  '
            else:
                st += '-  '
        print(st)


def brain_play():
    while 1:
        print('(if you want to quit, ENTER quit)')
        x = input("Your turn, please give a coordinate 'x y':")
        print()
        if x == 'quit':
            print('You quit.')
            return None
        x = x.split()
        try:
            brain_opponents(int(x[0]), int(x[1]))
        except ValueError or IndexError:
            print('Invalid input!')
            continue
        break
    # brain_show()
    return 0


def main():
    brain_init()
    brain_show()

    while brain_play() is not None:
        brain_turn()
        brain_show()


if __name__ == "__main__":
    pp = PP()
    main()
