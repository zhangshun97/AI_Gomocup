import time
import numpy as np


#
# a = np.array([1, 1, 1, 1, 0])
#
# dic = {
#     '11110': 4,
# }
# colour = 1
# empty = 0
# t1 = time.clock()
# x = list(a)
# # print(x.count(colour), x.count(empty))
# if x.count(colour) == 4 and x.count(empty) == 1:
#     y = [True, x.index(empty)]
# else:
#     y = [False]
# print(time.clock() - t1)
# print(y)
#
# t2 = time.clock()
# x = ''.join([str(i) for i in list(a)])
# if dic[x]:
#     y = [True, dic[x]]
# else:
#     y = [False]
# print(time.clock() - t2)
# print(y)

# def aa():
#     count = 0
#
#
#     def reset():
#         nonlocal count
#         count = 1
#     reset()
#     print(count)
#
# aa()

# aa = [(2, 7), (2, 7),(2, 7),(2, 7)]
# print(np.random.randint(len(aa)))

class role:

    def __init__(self):
        self.empty = 0
        self.AI = 1
        self.opp = 2

    def get_opponent(self, r):
        if not r:
            assert 0, "empty has no opponent"
        if r == self.AI:
            return self.opp
        else:
            return self.AI


R = role()

score = {
    'ONE': 10,
    'TWO': 100,
    'THREE': 1000,
    'FOUR': 100000,
    'FIVE': 10000000,
    'BLOCKED_ONE': 1,
    'BLOCKED_TWO': 10,
    'BLOCKED_THREE': 100,
    'BLOCKED_FOUR': 10000
}

debug = False

board1_1 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 1, 2, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 2, 2, 2, 2, 2, 1, 0, 1, 0, 0, 0, 0, 0],
    [1, 2, 1, 1, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

board1_2 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


# evaluate for a certain position
# not for the whole board

# return the score after taking this step
# a direction param is added for accelerating
#    if given direction, then only the direction will be checked


def evaluate_position(board1, position, player, direction=-1):
    result = 0
    # radius = 8
    count = 0
    block = 0
    empty = -1
    secondCount = 0  # count for another direction

    size = len(board1[0])

    def reset():
        nonlocal count, block, empty, secondCount
        count = 1
        block = 0
        empty = -1
        secondCount = 0  # count for another direction

    # --
    if direction == -1 or direction == 0:  # direction = undefined or 0
        reset()

        for i in range(position[1] + 1, size + 1):
            if i >= size:
                block += 1
                break

            t = board1[position[0]][i]
            if t == R.empty:
                if empty == -1 and i < size - 1 and board1[position[0]][i + 1] == player:
                    empty = count
                    continue
                else:
                    break

            if t == player:
                count += 1
                continue
            else:
                block += 1
                break

        for i in range(position[1] - 1, -1, -1):
            if i < 0:
                block += 1
                break
            t = board1[position[0]][i]
            if t == R.empty:
                if empty == -1 and i > 0 and board1[position[0]][i - 1] == player:
                    empty = 0  # 0 because of moving from left to right
                    continue
                else:
                    break

            if t == player:
                secondCount += 1
                if empty != -1:
                    empty += 1
                continue
            else:
                block += 1
                break

        count += secondCount

        r = countToScore(count, block, empty)
        if debug:
            print(count, block, empty)
            print(r)
        result += r

    # |
    if direction == -1 or direction == 1:
        reset()

        for i in range(position[0] + 1, size + 1):
            if i >= size:
                break

            t = board1[i][position[1]]
            if t == R.empty:
                if empty == -1 and i < size - 1 and board1[i + 1][position[1]] == player:
                    empty = count
                    continue
                else:
                    break

            if t == player:
                count += 1
                continue
            else:
                block += 1
                break

        for i in range(position[0] - 1, -1, -1):
            if i < 0:
                block += 1
                break
            t = board1[i][position[1]]
            if t == R.empty:
                if empty == -1 and i > 0 and board1[i - 1][position[1]] == player:
                    empty = 0
                    continue
                else:
                    break

            if t == player:
                secondCount += 1
                if empty != -1:
                    empty += 1
                    continue
            else:
                block += 1
                break

        count += secondCount

        r = countToScore(count, block, empty)
        if debug:
            print(count, block, empty)
            print(r)
        result += r

    # \
    if direction == -1 or direction == 2:
        reset()

        for i in range(1, size + 1):
            x = position[0] + i
            y = position[1] + i
            if x >= size or y >= size:
                block += 1
                break

            t = board1[x][y]
            if t == R.empty:
                if empty == -1 and x < size - 1 and y < size - 1 \
                        and board1[x + 1][y + 1] == player:
                    empty = count
                    continue
                else:
                    break

            if t == player:
                count += 1
                continue
            else:
                block += 1
                break

        for i in range(1, size + 1):
            x = position[0] - i
            y = position[1] - i
            if x < 0 or y < 0:
                block += 1
                break

            t = board1[x][y]
            if t == R.empty:
                if empty == -1 and x > 0 and y > 0 and board1[x - 1][y - 1] == player:
                    empty = 0
                    continue
                else:
                    break

            if t == player:
                secondCount += 1
                if empty != -1:
                    empty += 1
                continue
            else:
                block += 1
                break

        count += secondCount

        r = countToScore(count, block, empty)
        if debug:
            print(count, block, empty)
            print(r)
        result += r

    # /
    if direction == -1 or direction == 3:
        reset()

        for i in range(1, size + 1):
            x = position[0] + i
            y = position[1] - i
            if y < 0 or x >= size:
                block += 1
                break

            t = board1[x][y]
            if t == R.empty:
                if empty == -1 and x < size - 1 and y > 0 and board1[x + 1][y - 1] == player:
                    empty = count
                    continue
                else:
                    break

            if t == player:
                count += 1
                continue
            else:
                block += 1
                break

        for i in range(1, size + 1):
            x = position[0] - i
            y = position[1] + i
            if x < 0 or y >= size:
                block += 1
                break

            t = board1[x][y]
            if t == R.empty:
                if empty == -1 and x > 0 and y < size - 1 and board1[x - 1][y + 1] == player:
                    empty = 0
                    continue
                else:
                    break

            if t == player:
                secondCount += 1
                if empty != -1:
                    empty += 1
                continue
            else:
                block += 1
                break

        count += secondCount

        r = countToScore(count, block, empty)
        if debug:
            print(count, block, empty)
            print(r)
        result += r

    return result


def countToScore(count, block, empty=None):
    if empty is None:
        empty = 0

    # no vacancy
    if empty <= 0:
        if count >= 5:
            return score['FIVE']
        if block == 0:
            if count == 1:
                return score['ONE']
            if count == 2:
                return score['TWO']
            if count == 3:
                return score['THREE']
            if count == 4:
                return score['FOUR']
        elif block == 1:
            if count == 1:
                return score['BLOCKED_ONE']
            if count == 2:
                return score['BLOCKED_TWO']
            if count == 3:
                return score['BLOCKED_THREE']
            if count == 4:
                return score['BLOCKED_FOUR']
    elif empty == 1 or empty == count - 1:
        # the first square is empty
        if count >= 6:
            return score['FIVE']
        if block == 0:
            if count == 2:
                return score['TWO'] / 2
            if count == 3:
                return score['THREE']
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['FOUR']
        elif block == 1:
            if count == 2:
                return score['BLOCKED_TWO']
            if count == 3:
                return score['BLOCKED_THREE']
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['BLOCKED_FOUR']
    elif empty == 2 or empty == count - 2:
        # the second square is empty
        if count >= 7:
            return score['FIVE']
        if block == 0:
            if count == 3:
                return score['THREE']
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['BLOCKED_FOUR']
            if count == 6:
                return score['FOUR']
        elif block == 1:
            if count == 3:
                return score['BLOCKED_THREE']
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['BLOCKED_FOUR']
            if count == 6:
                return score['FOUR']
        elif block == 2:
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['BLOCKED_FOUR']
            if count == 6:
                return score['BLOCKED_FOUR']
    elif empty == 3 or empty == count - 3:
        if count >= 8:
            return score['FIVE']
        if block == 0:
            if count == 4:
                return score['THREE']
            if count == 5:
                return score['THREE']
            if count == 6:
                return score['BLOCKED_FOUR']
            if count == 7:
                return score['FOUR']
        elif block == 1:
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['BLOCKED_FOUR']
            if count == 6:
                return score['BLOCKED_FOUR']
            if count == 7:
                return score['FOUR']
        elif block == 2:
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['BLOCKED_FOUR']
            if count == 6:
                return score['BLOCKED_FOUR']
            if count == 7:
                return score['BLOCKED_FOUR']
    elif empty == 4 or empty == count - 4:
        if count >= 9:
            return score['FIVE']
        if block == 0:
            if count == 5:
                return score['FOUR']
            if count == 6:
                return score['FOUR']
            if count == 7:
                return score['FOUR']
            if count == 8:
                return score['FOUR']
        elif block == 1:
            if count == 4:
                return score['BLOCKED_FOUR']
            if count == 5:
                return score['BLOCKED_FOUR']
            if count == 6:
                return score['BLOCKED_FOUR']
            if count == 7:
                return score['BLOCKED_FOUR']
            if count == 8:
                return score['FOUR']
        elif block == 2:
            if count == 5:
                return score['BLOCKED_FOUR']
            if count == 6:
                return score['BLOCKED_FOUR']
            if count == 7:
                return score['BLOCKED_FOUR']
            if count == 8:
                return score['BLOCKED_FOUR']
    elif empty == 5 or empty == count - 5:
        return score['FIVE']

    return 0


board1 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
a = [0, 1, 2]
pointCache = {}
hhh = True
if hhh:
    for i1 in a:
        for i2 in a:
            for i3 in a:
                for i4 in a:
                    for i5 in a:
                        for i6 in a:
                            for i7 in a:
                                for i8 in a:
                                    for i9 in a:
                                        for i10 in a:
                                            board1 = [
                                                [i1, i2, i3, i4, i5, 0, i6, i7, i8, i9, i10],
                                            ]
                                            point_1 = evaluate_position(board1, position=(0, 5), player=1, direction=0)
                                            point_2 = evaluate_position(board1, position=(0, 5), player=2, direction=0)
                                            i1_ = 103 if i1 == 2 else i1*100
                                            i2_ = 103 if i2 == 2 else i2*100
                                            i3_ = 103 if i3 == 2 else i3*100
                                            i4_ = 103 if i4 == 2 else i4*100
                                            i5_ = 103 if i5 == 2 else i5*100
                                            i6_ = 103 if i6 == 2 else i6*100
                                            i7_ = 103 if i7 == 2 else i7*100
                                            i8_ = 103 if i8 == 2 else i8*100
                                            i9_ = 103 if i9 == 2 else i9*100
                                            i10_ = 103 if i10 == 2 else i10*100
                                            # pattern = i1 * 10 ** 9 + i2 * 10 ** 8 + i3 * 10 ** 7 + \
                                            #           i4 * 10 ** 6 + i5 * 10 ** 5 + i6 * 10 ** 4 + \
                                            #           i7 * 10 ** 3 + i8 * 10 ** 2 + i9 * 10 + i10
                                            pattern = i1_ + i2_ * 10 + i3_ * 10 ** 2 + \
                                                      i4_ * 10 ** 3 + i5_ * 10 ** 4 + i6_ * 10 ** 4 + \
                                                      i7_ * 10 ** 3 + i8_ * 10 ** 2 + i9_ * 10 + i10_
                                            # if pattern < 13.06:
                                            #     print(pattern)
                                            #     print(board1)
                                            #     print(point_1, point_2)
                                            pointCache[pattern] = (point_1, point_2)

    with open('pointCache.txt', 'w') as f:
        f.write(str(pointCache))

with open('pointCache.txt', 'r') as f:
    a = f.read()
    dic = eval(a)

    i1, i2, i3, i4, i5, _, i6, i7, i8, i9, i10 = 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2
    i1 = 1.03 if i1 == 2 else i1
    i2 = 1.03 if i2 == 2 else i2
    i3 = 1.03 if i3 == 2 else i3
    i4 = 1.03 if i4 == 2 else i4
    i5 = 1.03 if i5 == 2 else i5
    i6 = 1.03 if i6 == 2 else i6
    i7 = 1.03 if i7 == 2 else i7
    i8 = 1.03 if i8 == 2 else i8
    i9 = 1.03 if i9 == 2 else i9
    i10 = 1.03 if i10 == 2 else i10
    # pattern = i1 * 10 ** 9 + i2 * 10 ** 8 + i3 * 10 ** 7 + \
    #           i4 * 10 ** 6 + i5 * 10 ** 5 + i6 * 10 ** 4 + \
    #           i7 * 10 ** 3 + i8 * 10 ** 2 + i9 * 10 + i10
    pattern = i1 + i2 * 10 + i3 * 10 ** 2 + \
              i4 * 10 ** 3 + i5 * 10 ** 4 + i6 * 10 ** 4 + \
              i7 * 10 ** 3 + i8 * 10 ** 2 + i9 * 10 + i10
    print(pattern)
    print(dic[1206])
# board1 = [
#     [0, 0, 0, 1, 0, 0, 1, 1, 0, 2, 0],
# ]
# print(evaluate_position(board1, position=(0, 5), player=1, direction=0))
