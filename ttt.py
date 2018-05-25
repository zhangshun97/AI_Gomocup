board = [[0 for i in range(20)] for j in range(20)]

# check if win
x_this, y_this = (19, 1)
# \
# get the boundaries
up = min(x_this, 4)
down = min(19 - x_this, 4)
left = min(y_this, 4)
right = min(19 - y_this, 4)
# \
for i in range(up + down - 3):
    a = [
        board[x_this - up + i + j][y_this] for j in range(5)
    ]
    b = [
        (x_this - up + i + j, y_this) for j in range(5)
    ]
    assert len(a) == 5, "error when check if win on board"
    print(a)
    print(b)
