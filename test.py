import random
import copy
import math as np
import time

MAX_BOARD = 6  # zs: just for testing
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


class Board:

    def __init__(self, input_board, n_in_line=5):
        assert type(n_in_line) == int, "n_in_line para should be INT!"
        self.width = len(input_board[0])
        self.height = len(input_board)
        self.board = copy.deepcopy(input_board)
        self.n_in_line = n_in_line
        self.availables = [
            (i, j) for i in range(self.height) for j in range(self.width) if input_board[i][j] == 0
        ]
        self.winner = None

    def is_free(self, x, y):
        return 1 if self.board[x][y] == 0 else 0

    def update(self, player, move):
        """
        update the board and check if player wins, so one should use like this:
            if board.update(player, move):
                winner = board.winner
        :param player: the one to take the move
        :param move: a tuple (x, y)
        :return: 1 denotes player wins and 0 denotes not
        """
        assert len(move) == 2, "move is invalid, len = {}".format(len(move))
        self.board[move[0]][move[1]] = player
        self.availables.remove(move)

        """check if player win"""
        x_this, y_this = move
        # get the boundaries
        up = min(x_this, self.n_in_line - 1)
        down = min(self.height - 1 - x_this, self.n_in_line - 1)
        left = min(y_this, self.n_in_line - 1)
        right = min(self.width - 1 - y_this, self.n_in_line - 1)
        # \
        up_left = min(up, left)
        down_right = min(down, right)
        for i in range(up_left + down_right - self.n_in_line + 2):
            a = [
                self.board[x_this - up_left + i + j][y_this - up_left + i + j] for j in range(self.n_in_line)
            ]
            assert len(a) == self.n_in_line, "error when check if win on board"
            if len(set(a)) == 1 and a[0] > 0:
                self.winner = player
                return 1
        # /
        up_right = min(up, right)
        down_left = min(down, left)
        for i in range(up_right + down_left - self.n_in_line + 2):
            a = [
                self.board[x_this - up_right + i + j][y_this + up_right - i - j] for j in range(self.n_in_line)
            ]
            assert len(a) == self.n_in_line, "error when check if win on board"
            if len(set(a)) == 1 and a[0] > 0:
                self.winner = player
                return 1
        # --
        for i in range(left + right - self.n_in_line + 2):
            a = [
                self.board[x_this][y_this - left + i + j] for j in range(self.n_in_line)
            ]
            assert len(a) == self.n_in_line, "error when check if win on board"
            if len(set(a)) == 1 and a[0] > 0:
                self.winner = player
                return 1
        # |
        for i in range(up + down - self.n_in_line + 2):
            a = [
                self.board[x_this - up + i + j][y_this] for j in range(self.n_in_line)
            ]
            assert len(a) == self.n_in_line, "error when check if win on board"
            if len(set(a)) == 1 and a[0] > 0:
                self.winner = player
                return 1
        # no one wins
        return 0


class MCTS:

    def __init__(self, input_board, players_in_turn, n_in_line=5, confidence=2, time_limit=5.0, max_simulation=10):
        self.time_limit = float(time_limit)
        self.max_simulation = max_simulation
        self.MCTSboard = Board(input_board, n_in_line)  # a deep copy Board class object
        self.confidence = confidence                    # confidence level of exploration
        self.player_turn = players_in_turn
        self.player = self.player_turn[0]               # always the AI first when calling this Algorithm
        self.plays = dict()                             # to record the number of simulations of a node
        self.wins = dict()                              # to record the number of winnings of a node
        self.max_depth = 1
        # self.tree = dict()

    def get_player(self, play_turn):
        """play one by one"""
        p = play_turn.pop(0)
        play_turn.append(p)
        return p

    def get_action(self):
        if len(self.MCTSboard.availables) == 1:
            return self.MCTSboard.availables[0]  # the only choice

        self.plays = dict()
        self.wins = dict()
        simulations = 0
        begin_time = time.time()
        while time.time() - begin_time < self.time_limit:
            # run MCTS
            board_deep_copy = copy.deepcopy(self.MCTSboard)
            fixed_play_turn = copy.deepcopy(self.player_turn)
            self.run_simulations(board_deep_copy, fixed_play_turn)
            simulations += 1
        print("total simulations in one action:{}".format(simulations))

        move = self.select_one_move()
        print('Maximum depth searched in one action:', self.max_depth)

        return move

    def select_one_move(self):
        percent_wins, move = max(
            (self.wins.get((self.player, move), 0) /
             self.plays.get((self.player, move), 1),
             move)
            for move in self.MCTSboard.availables)  # choose a move with highest winning rate

        return move

    def run_simulations(self, cur_board, play_turn):
        plays = self.plays
        wins = self.wins
        availables = cur_board.availables

        player = self.get_player(play_turn)  # which player this turn
        visited_states = set()  # record all the moves
        winner = -1
        expand = True

        print('=' * 50)
        # Simulation
        for t in range(1, self.max_simulation + 1):
            # Selection
            # 如果所有着法都有统计信息，则获取UCB最大的着法
            if all(plays.get((player, move)) for move in availables):
                log_total = np.log(
                    sum([plays[(player, move)] for move in availables]))
                value, move = max(
                    ((wins[(player, move)] / plays[(player, move)]) +
                     np.sqrt(self.confidence * log_total / plays[(player, move)]), move)
                    for move in availables)
                print(wins[(player, move)], value, move)
                print('-' * 40, player)
            else:
                # 否则随机选择一个着法
                move = random.choice(availables)
                print(move)

            win = cur_board.update(player, move)
            # DEBUG
            # if t % 5 == 0:
            print('-' * 40)
            for row in cur_board.board:
                print(' '.join([str(i) for i in row]))

            # Expand
            # 每次模拟最多扩展一次，每次扩展只增加一个着法
            if expand and (player, move) not in plays:
                expand = False
                plays[(player, move)] = 0
                wins[(player, move)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, move))

            is_full = not len(availables)
            if is_full or win:  # 游戏结束，没有落子位置或有玩家获胜
                # print('-' * 40)
                # for row in cur_board.board:
                #     print(' '.join([str(i) for i in row]))
                break  # checked

            player = self.get_player(play_turn)

        # Back-propagation
        for player, move in visited_states:
            if (player, move) not in plays.keys():
                continue
            plays[(player, move)] += 1  # 当前路径上所有着法的模拟次数加1
            if player == winner:
                wins[(player, move)] += 1  # 获胜玩家的所有着法的胜利次数加1


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


def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")


def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
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

    MCTS_AI = MCTS(board,
                   players_in_turn=[1, 2],  # brain is 1
                   n_in_line=4,
                   confidence=2,
                   time_limit=0.3,
                   max_simulation=200)
    i = 0
    while True:
        move = MCTS_AI.get_action()
        x, y = move
        if MCTS_AI.MCTSboard.winner:
            print("Winner: {}".format(MCTS_AI.MCTSboard.winner))
            break

        if pp.terminateAI:
            return

        if isFree(x, y):
            break
    if i > 1:
        # zs: maybe useful to debug
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    pp.do_mymove(x, y)


def brain_end(x, y):
    pass


def brain_about():
    pp.pipeOut(pp.infotext)


def brain_show():
    for row in board:
        print(' '.join([str(i) for i in row]))


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
    return 1


def main():
    brain_init()
    brain_show()

    while brain_play() is not None:
        brain_turn()
        brain_show()


if __name__ == "__main__":
    pp = PP()
    main()
