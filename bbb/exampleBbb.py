import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
from ai import AI
from config import Config
import time
from score import score

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", ' \
              'country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

myAI = None
config = Config()



def brain_init():
    # zs: here pp.width and pp.height are default as 20
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

    if not if_only:
        move_vcx = myAI.get_move_vcx()
        if move_vcx:
            myAI.if_found_vcx = True
            # print('HHHHHHH')
            move = move_vcx

    myAI.set(move, 1)
    x, y = move
    pp.do_mymove(x, y)


def brain_end():
    pass


def brain_about():
    pp.pipeOut(pp.infotext)


if DEBUG_EVAL:
    import win32gui


    def brain_eval(x, y):
        # TODO check if it works as expected
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
    pp.brain_eval = brain_eval


def main():
    pp.main()


if __name__ == "__main__":
    main()