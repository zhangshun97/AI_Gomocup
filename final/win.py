from role import role

R = role()


# 判断 player 下了这个点之后有没有成 5
def isFive(b, p, player):
    size = b.size
    count = 1

    def reset():
        count = 1

    # --
    i = p[1] + 1
    while 1:
        if i >= size:
            break
        t = b.board[p[0]][i]
        if t != player:
            break
        count += 1
        i += 1
    i = p[1] - 1
    while 1:
        if i < 0:
            break
        t = b.board[p[0]][i]
        if t != player:
            break
        count += 1
        i -= 1

    if count >= 5:
        return True

    # |
    reset()
    i = p[0] + 1
    while 1:
        if i >= size:
            break
        t = b.board[i][p[1]]
        if t != player:
            break
        count += 1
        i += 1
    i = p[0] - 1
    while 1:
        if i < 0:
            break
        t = b.board[i][p[1]]
        if t != player:
            break
        count += 1
        i -= 1

    if count >= 5:
        return True

    # \
    reset()

    i = 1
    while 1:
        x, y = p[0] + i, p[1] + i
        if x >= size or y >= size:
            break
        t = b.board[x][y]
        if t != player:
            break
        count += 1
        i += 1
    i = 1
    while 1:
        x, y = p[0] - i, p[1] - i
        if x < 0 or y < 0:
            break
        t = b.board[x][y]
        if t != player:
            break
        count += 1
        i += 1

    if count >= 5:
        return True

    # /
    reset()

    i = 1
    while 1:
        x, y = p[0] + i, p[1] - i
        if x >= size or y < 0:
            break
        t = b.board[x][y]
        if t != player:
            break
        count += 1
        i += 1
    i = 1
    while 1:
        x, y = p[0] - i, p[1] + i
        if x < 0 or y >= size:
            break
        t = b.board[x][y]
        if t != player:
            break
        count += 1
        i += 1

    if count >= 5:
        return True

    return False
