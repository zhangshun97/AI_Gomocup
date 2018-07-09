import time
import numpy as np
from pointCache import pointCache as dic


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

from role import role

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

straight = {
    0: 0,
    1: score['ONE'],
    2: score['TWO'],
    3: score['THREE'],
    4: score['FOUR'],
    5: score['FIVE'],
}
blocked = {
    0: 0,
    1: score['BLOCKED_ONE'],
    2: score['BLOCKED_TWO'],
    3: score['BLOCKED_THREE'],
    4: score['BLOCKED_FOUR'],
    5: score['BLOCKED_FOUR'],
    6: score['BLOCKED_FOUR'],
    7: score['BLOCKED_FOUR'],
    8: score['BLOCKED_FOUR'],
    9: score['BLOCKED_FOUR'],
    10: score['BLOCKED_FOUR'],
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


"hhh, 不用考虑效率问题真舒服"


def evaluate_position(board1, position, player, direction=-1):
    result = 0
    radius = 6

    size = len(board1[0])

    # --
    if direction == -1 or direction == 0:  # direction = undefined or 0

        maxLong = 1
        # find max long
        for i in range(1, radius):
            x, y = position[0], position[1] + i
            if y >= size or board1[x][y] == R.get_opponent(player):
                break
            maxLong += 1
        for i in range(1, radius):
            x, y = position[0], position[1] - i
            if y < 0 or board1[x][y] == R.get_opponent(player):
                break
            maxLong += 1

        # print(maxLong)

        continueLength = 1
        # find continue length
        for i in range(1, radius):
            x, y = position[0], position[1] + i
            if y >= size or board1[x][y] != player:
                break
            continueLength += 1
        for i in range(1, radius):
            x, y = position[0], position[1] - i
            if y < 0 or board1[x][y] != player:
                break
            continueLength += 1

        # print(continueLength)

        emptyR = 0
        selfAgainCountR = 0
        # find right pattern
        for i in range(1, radius):
            x, y = position[0], position[1] + i
            if y >= size or board1[x][y] == R.get_opponent(player):
                break
            if board1[x][y] == R.empty:
                if not selfAgainCountR:
                    emptyR += 1
                    continue
                else:
                    break
            if emptyR == 1 and board1[x][y] == player:
                selfAgainCountR += 1

        emptyL = 0
        selfAgainCountL = 0
        # find left pattern
        for i in range(1, radius):
            x, y = position[0], position[1] - i
            if y < 0 or board1[x][y] == R.get_opponent(player):
                break
            if board1[x][y] == R.empty:
                if not selfAgainCountL:
                    emptyL += 1
                    continue
                else:
                    break

            if emptyL == 1 and board1[x][y] == player:
                selfAgainCountL += 1

        blockR = 0
        # find right block
        for i in range(1, radius):
            x, y = position[0], position[1] + i
            if y >= size:
                break
            if position[1] + 1 < size and board1[position[0]][position[1] + 1] == R.get_opponent(player):
                blockR = 1
                break
            if board1[x][y - 1] == player and board1[x][y] == R.get_opponent(player):
                blockR = 1
                break

        blockL = 0
        # find left block
        for i in range(1, radius):
            x, y = position[0], position[1] - i
            if y < 0:
                break
            if position[1] - 1 >= 0 and board1[position[0]][position[1] - 1] == R.get_opponent(player):
                blockL = 1
                break
            if board1[x][y + 1] == player and board1[x][y] == R.get_opponent(player):
                blockL = 1
                break

        # print(
        #     'maxLong', maxLong, '\n',
        #     'continueLength', continueLength, '\n',
        #     'selfAgainCountL', selfAgainCountL, '\n',
        #     'selfAgainCountR', selfAgainCountR, '\n',
        #     'blockL', blockL, '\n',
        #     'blockR', blockR, '\n',
        #     'emptyL', emptyL, '\n',
        #     'emptyR', emptyR, '\n',
        # )
        if maxLong < 5:
            return 0
        result = countToScore(continueLength,
                                         selfAgainCountL, selfAgainCountR, blockL, blockR, emptyL, emptyR)
        if maxLong == 5 and continueLength < 4:
            return result // 2  # 2011102 < 0011102

    return result


def countToScore(continueLength, selfAgainCountL, selfAgainCountR, blockL, blockR, emptyL, emptyR):

    hhh = 5
    # 成五直接返回
    if continueLength >= 5:
        return score['FIVE']

    if not blockL and not blockR:
        # 两边都没有以 '12' 堵住
        if selfAgainCountL and selfAgainCountR:
            return straight[max(selfAgainCountL, selfAgainCountR)] + blocked[min(selfAgainCountL, selfAgainCountR)]
        elif selfAgainCountL:
            if selfAgainCountL + continueLength <= 3:
                return straight[selfAgainCountL + continueLength]
            else:
                return blocked[4]
        elif selfAgainCountR:
            if selfAgainCountR + continueLength <= 3:
                return straight[selfAgainCountR + continueLength]
            else:
                return blocked[4]
        else:
            return straight[continueLength] + hhh
    elif blockL and not blockR:
        # 左边是 '21' 且右边至少是 '02' 的情形
        if not emptyL:
            # 左边没有空 '2111--'
            return blocked[continueLength + selfAgainCountR]
        else:
            if emptyL == 1:
                return blocked[continueLength + selfAgainCountL]
            else:
                if emptyR > 1:
                    return straight[continueLength] + blocked[selfAgainCountR]
                else:
                    return (straight[continueLength] + blocked[selfAgainCountR]) // 2
    elif blockR and not blockL:
        # 右边是 '12' 且左边至少是 '20' 的情形
        if not emptyR:
            # 右边没有空 '--1112'
            return blocked[continueLength + selfAgainCountL]
        else:
            if emptyR == 1:
                return blocked[continueLength + selfAgainCountR]
            else:
                if emptyL > 1:
                    return straight[continueLength] + blocked[selfAgainCountL]
                else:
                    return (straight[continueLength] + blocked[selfAgainCountL]) // 2
    else:
        # 两边都被堵住了
        if emptyL and emptyR:
            return straight[continueLength]
        elif emptyR:
            return blocked[continueLength + selfAgainCountR]
        elif emptyL:
            return blocked[continueLength + selfAgainCountL]
        else:
            return 0
        #注意，这里没有两边都是非空的情况！


board1 = [
    [0, 2, 2, 1, 1, 0, 1, 1, 1, 2, 2],
    #               /\
    #               ||
]
print(evaluate_position(board1, position=(0, 5), player=1, direction=0))


board1 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
a = [0, 1, 2]
pointCache = {}
hhh = False
mm = 3
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
                                            # i1_ = R.oppp if i1 == 2 else i1*R.AIp
                                            # i2_ = R.oppp if i2 == 2 else i2*R.AIp
                                            # i3_ = R.oppp if i3 == 2 else i3*R.AIp
                                            # i4_ = R.oppp if i4 == 2 else i4*R.AIp
                                            # i5_ = R.oppp if i5 == 2 else i5*R.AIp
                                            # i6_ = R.oppp if i6 == 2 else i6*R.AIp
                                            # i7_ = R.oppp if i7 == 2 else i7*R.AIp
                                            # i8_ = R.oppp if i8 == 2 else i8*R.AIp
                                            # i9_ = R.oppp if i9 == 2 else i9*R.AIp
                                            # i10_ = R.oppp if i10 == 2 else i10*R.AIp
                                            pattern = i1 * mm ** 10 + i2 * mm ** 9 + i3 * mm ** 8 + \
                                                      i4 * mm ** 7 + i5 * mm ** 6 + i6 * mm ** 4 + \
                                                      i7 * mm ** 3 + i8 * mm ** 2 + i9 * mm + i10
                                            # pattern = i1_ * 10 ** 9 + i2_ * 10 ** 8 + i3_ * 10 ** 7 + \
                                            #           i4_ * 10 ** 6 + i5_ * 10 ** 5 + i6_ * 10 ** 4 + \
                                            #           i7_ * 10 ** 3 + i8_ * 10 ** 2 + i9_ * 10 + i10_
                                            # if pattern < 13.06:
                                            #     print(pattern)
                                            #     print(board1)
                                            #     print(point_1, point_2)
                                            # if tuple(board1[0]) == (0, 0, 2, 0, 0, 0, 1, 1, 1, 2, 0):
                                            # if point_1 == 0:
                                            #     print(board1[0], point_1)
                                            pointCache[pattern] = (point_1, point_2)
                                            #####
                                            pattern = i1 * mm ** 10 + i2 * mm ** 9 + i3 * mm ** 8 + \
                                                      i4 * mm ** 7 + i5 * mm ** 6 + i6 * mm ** 4 + \
                                                      i7 * mm ** 3 + i8 * mm ** 2 + i9 * mm + i10 + R.AI * mm ** 5

                                            pointCache[pattern] = (point_1, 0)
                                            pattern = i1 * mm ** 10 + i2 * mm ** 9 + i3 * mm ** 8 + \
                                                      i4 * mm ** 7 + i5 * mm ** 6 + i6 * mm ** 4 + \
                                                      i7 * mm ** 3 + i8 * mm ** 2 + i9 * mm + i10 + R.opp * mm ** 5

                                            pointCache[pattern] = (0, point_2)

    with open('pointCache.txt', 'w') as f:
        f.write(str(pointCache))
    print(len(pointCache.keys()))

# with open('pointCache.txt', 'r') as f:
#     a = f.read()
#     dic = eval(a)

i1, i2, i3, i4, i5, _, i6, i7, i8, i9, i10 = 0, 0, 2, 0, 0, 0, 1, 1, 1, 2, 0
# i1_ = R.oppp if i1 == 2 else i1*R.AIp
# i2_ = R.oppp if i2 == 2 else i2*R.AIp
# i3_ = R.oppp if i3 == 2 else i3*R.AIp
# i4_ = R.oppp if i4 == 2 else i4*R.AIp
# i5_ = R.oppp if i5 == 2 else i5*R.AIp
# i6_ = R.oppp if i6 == 2 else i6*R.AIp
# i7_ = R.oppp if i7 == 2 else i7*R.AIp
# i8_ = R.oppp if i8 == 2 else i8*R.AIp
# i9_ = R.oppp if i9 == 2 else i9*R.AIp
# i10_ = R.oppp if i10 == 2 else i10*R.AIp
pattern = i1 * mm ** 10 + i2 * mm ** 9 + i3 * mm ** 8 + \
          i4 * mm ** 7 + i5 * mm ** 6 + i6 * mm ** 4 + \
          i7 * mm ** 3 + i8 * mm ** 2 + i9 * mm + i10
# pattern = i1_ * 10 ** 9 + i2_ * 10 ** 8 + i3_ * 10 ** 7 + \
#           i4_ * 10 ** 6 + i5_ * 10 ** 5 + i6_ * 10 ** 4 + \
#           i7_ * 10 ** 3 + i8_ * 10 ** 2 + i9_ * 10 + i10_
# print(pattern)
# print(dic[200104000])

