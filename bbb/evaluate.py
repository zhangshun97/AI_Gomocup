from role import role
from score import score

R = role()

# evaluate for a certain position
# not for the whole board

# return the score after taking this step
# a direction param is added for accelerating
#    if given direction, then only the direction will be checked


def evaluate_position(b, position, player, direction=-1):
    result = 0
    # radius = 8
    count = 0
    block = 0
    empty = -1
    secondCount = 0  # count for another direction
    board1 = b.board
    size = b.size

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

        b.scoreCache[player][0][position[0]][position[1]] = countToScore(count, block, empty)

    result += b.scoreCache[player][0][position[0]][position[1]]

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

        b.scoreCache[player][1][position[0]][position[1]] = countToScore(count, block, empty)

    result += b.scoreCache[player][1][position[0]][position[1]]

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

        b.scoreCache[player][2][position[0]][position[1]] = countToScore(count, block, empty)

    result += b.scoreCache[player][2][position[0]][position[1]]

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

        b.scoreCache[player][3][position[0]][position[1]] = countToScore(count, block, empty)

    result += b.scoreCache[player][3][position[0]][position[1]]

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
