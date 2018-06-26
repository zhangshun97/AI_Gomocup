from ai import AI
import time

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
# board[1][5] = 2
# board[1][6] = 1
# board[1][7] = 2
# board[2][6] = 1

myAI = None


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

    if pp.terminateAI:
        return

    global myAI
    if myAI.turnChecked:
        opp_move = myAI.get_opponent_move(board)
        myAI.set(opp_move, 2)
    else:
        myAI = AI(board)
        myAI.turnChecked = True
    t0 = time.clock()
    move = myAI.get_move()
    print(time.clock() - t0)
    myAI.set(move, 1)

    # x, y = input("AI move 'x y':").split()
    # x, y = int(x), int(y)
    # myAI.set((x, y), 1)
    # print("AI score: {}".format(myAI.theBoard.evaluate(1)))
    # print("Hum score: {}".format(myAI.theBoard.evaluate(2)))

    x, y = move
    pp.do_mymove(x, y)


def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return

    global myAI
    myAI = AI(board)

    pp.pipeOut("OK")


def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0

    global myAI
    myAI = AI(board)

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