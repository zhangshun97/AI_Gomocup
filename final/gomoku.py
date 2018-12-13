from ai import AI
from config import Config
from score import score
import time
import argparse

parser = argparse.ArgumentParser(description='DC-GAN on PyTorch')
parser.add_argument('--board-size', default=15,
                    help='board size, assuming the board is a square', type=int)
parser.add_argument('--first', default='me', type=str,
                    help="who first? 'me' for player, 'ai' for AI")
args = parser.parse_args()

MAX_BOARD = args.board_size
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


config = Config()
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
        if myAI.white_or_black():
            myAI.searchDeep = config.searchDeep_black
        else:
            myAI.searchDeep = config.searchDeep_white
        myAI.searchDeep_ = myAI.searchDeep
        myAI.turnChecked = True
    
    if myAI.turnChecked and len(myAI.theBoard.allSteps) <= 4:
        myAI.searchDeep = myAI.searchDeep_ - 2
    else:
        myAI.searchDeep = myAI.searchDeep_

    myAI.theBoard.startTime = time.clock()

    if_only = False
    if not myAI.if_found_vcx:
        # 如果之前已经找到，之后就不需要再搜了
        move, if_only = myAI.get_move()
    # print(time.clock() - myAI.theBoard.startTime)
    if not if_only:
        move_vcx = myAI.get_move_vcx()
        if move_vcx:
            myAI.if_found_vcx = True
            print('HHHHHHH, you are DEAD!!!')
            move = move_vcx
    print("time used: %.2f s" % (time.clock() - myAI.theBoard.startTime))
    myAI.set(move, 1)
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
    if args.first == 'ai':
        brain_turn()
    elif args.first == 'me':
        pass
    else:
        raise ValueError("Argument 'first' should be either 'me' or 'ai'!")
    brain_show()

    while brain_play() is not None:
        brain_turn()
        brain_show()


if __name__ == "__main__":
    pp = PP()
    main()
