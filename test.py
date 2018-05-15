import random


MAX_BOARD = 10  # zs: just for testing
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


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
    """my turn: take a step randomly"""
    if pp.terminateAI:
        return
    i = 0
    while True:
        x = random.randint(0, pp.width)
        y = random.randint(0, pp.height)
        i += 1
        if pp.terminateAI:
            return
        if isFree(x, y):
            break
    if i > 1:
        # zs: ???
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    # pp.do_mymove(x, y)
    pp.do_oppmove(x, y)


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
            brain_my(int(x[0]), int(x[1]))
        except ValueError and IndexError:
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
