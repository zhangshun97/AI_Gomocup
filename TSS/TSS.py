## TO RUN THIS PROGRAM, DON'T FORGET TO INSTALL DEPENDENCIES
## IF USING PYTHON 3.6.2, USE PIP3 INSTALL INSTEAD OF PIP INSTALL
import numpy as np
import random
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
import copy

MAX_BOARD = 10
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
empty = 0


class Board:
    def __init__(self, list_list_board, AI, players):
        # Initialise a  board
        self.board = np.array(list_list_board)
        self.height, self.width = len(list_list_board), len(list_list_board[0])
        assert self.height == self.width, "The board is a rectangular!"
        self.size = self.height
        self.AI = AI(players)
        self.players = players
        self.AI_c = self.players[0]
        self.opponent = self.players[1]
        self.found_sol = False
        self.sol_seq = []

        self.turn = 1

    def get_next_move(self, opp_move=None):
        if opp_move is not None:
            row, col = opp_move
            if self.board[row, col] != empty:
                print("The position has been occupied!")
            self.board[row, col] = self.opponent

        if np.sum(self.board) < 1:  # the board is empty and AI first
            return self.height // 2, self.width // 2

        self.turn += 1

        if self.found_sol:
            if len(self.sol_seq) > 0:
                AI_pos = self.sol_seq.pop(0)
            else:
                x = self.AI.find_threats(5, self.opponent, self.size, self.board)
                y = self.AI.find_threats(6, self.opponent, self.size, self.board)
                z = self.AI.find_threats(7, self.opponent, self.size, self.board)

                if x or y or z:
                    if x:
                        if not y and z:
                            merged_threat = {**x, **z}
                        elif y and not z:
                            merged_threat = {**x, **y}
                        elif y and z:
                            merged_threat = {**x, **y, **z}
                        else:
                            merged_threat = x
                    else:
                        if not y and z:
                            merged_threat = z
                        elif y and not z:
                            merged_threat = y
                        elif y and z:
                            merged_threat = {**x, **y, **z}
                    # print(merged_threat)
                    v = list(merged_threat.values())
                    k = list(merged_threat.keys())
                    m = min(v)
                    indices = [i for i, j in enumerate(v) if j == m]
                    best_threat = []
                    for each in indices:
                        best_threat.append(k[each])
                    # print("Best Placements: ",best_threat)
                    AI_pos = random.choice(best_threat)
        # we will run the AI method here
        elif self.turn == 2:
            AI_pos = self.AI.maximise_own(self.board, self.opponent, self.AI_c, self.turn)
        else:
            x = self.AI.find_threats(5, self.opponent, self.size, self.board)
            y = self.AI.find_threats(6, self.opponent, self.size, self.board)
            z = self.AI.find_threats(7, self.opponent, self.size, self.board)

            if x or y or z:
                if x:
                    if not y and z:
                        merged_threat = {**x, **z}
                    elif y and not z:
                        merged_threat = {**x, **y}
                    elif y and z:
                        merged_threat = {**x, **y, **z}
                    else:
                        merged_threat = x
                else:
                    if not y and z:
                        merged_threat = z
                    elif y and not z:
                        merged_threat = y
                    elif y and z:
                        merged_threat = {**x, **y, **z}
                # print(merged_threat)
                v = list(merged_threat.values())
                k = list(merged_threat.keys())
                m = min(v)
                indices = [i for i, j in enumerate(v) if j == m]
                best_threat = []
                for each in indices:
                    best_threat.append(k[each])
                # print("Best Placements: ",best_threat)
                AI_pos = random.choice(best_threat)
            else:
                root_node = self.AI.node(None)
                sol = self.AI.threat_space_search(self.board, root_node, self.opponent, self.AI_c, self.size)

                if sol:
                    self.found_sol = True
                    self.sol_seq = sol[1:]
                    # print(self.sol_seq)
                    AI_pos = self.sol_seq.pop(0)
                else:
                    AI_pos = self.AI.maximise_own(self.board, self.opponent, self.AI_c, self.turn)

        return AI_pos


class AI:

    def __init__(self, players):
        self.get_opp = {
            players[0]: players[1],
            players[1]: players[0]
        }

    # Defining of all threat variations
    def four(self, array, colour):  # accepts an array of length 5
        x = list(array)
        # print(x.count(colour), x.count(empty))
        if x.count(colour) == 4 and x.count(empty) == 1:
            return [True, x.index(empty)]
        return [False]

    def broken_three(self, array, colour):
        # 010110 or 011010 (flip!) accepts array 6
        if array[0] == empty and array[1] == colour and \
                array[5] == empty and array[4] == colour:
            if array[2] == empty and array[3] == colour:
                return [True, 2]
            elif array[2] == colour and array[3] == empty:
                return [True, 3]
        return [False]

    def three(self, array, colour):  # accepts array 7

        # 0011100 or 2011100 or 0011102
        if array[2] == colour and array[3] == colour and array[4] == colour and array[5] == empty and array[1] == empty:
            if array[0] == empty and array[6] == empty:
                return [True, 1, 5]
            elif array[0] == self.get_opp[colour] and array[6] == empty:
                return [True, 1, 5, 6]
            elif array[0] == empty and array[6] == self.get_opp[colour]:
                return [True, 1, 5, 0]
        return [False]

    def straight_four(self, array, colour):
        if array[0] == empty and array[5] == empty and array[1] == colour and \
                array[2] == colour and array[3] == colour and array[4] == colour:
            return True
        return False

    def five(self, array, colour):
        x = list(array)
        if x.count(colour) == 5:
            return True
        return False

    # This AI will decide a move based on the following order of steps:
    # (0) -> If AI can win this turn, AI does so
    # (1) -> Check for opponent's threats and prevent them (the straight_four
    # threat cannot be prevented so we will not check for this threat type)
    # (2) -> Form a winning threat-sequence independent of opponent's movement
    #        (we will ignore the proof-number search for now and allow opponent
    #        to place seeds on all cost squares)
    # (3) -> Prevent opponent from forming a threat (prevention is better than
    #        cure). There may be multiple squares to prevent multiple threats
    #        so we count all and see which square has the most occurances. This
    #        can be done by treating own colour as opponent. If placing on a
    #        square results in a threat being formed, then that square is a
    #        prevention square.
    # (4) -> Lastly, we will place our seed where our seeds are most in-line.
    #        Calculation: total seeds in-line excluding where seed is placed.
    #        If turn 1 => place beside opponent's. Also if multiple squares
    #        have equal total, randomly select a square.

    ###################
    ## Section (0+1) ##
    ###################

    def threat_algo(self, array, colour, length):
        ## colour = player's colour by default
        opp = self.get_opp[colour]
        if length == 5:
            # print(array)
            x = self.four(array, opp)
            if x[0]:
                x.append(1)
                return x
            x = self.four(array, colour)
            if x[0]:
                x.append(2)
                return x
        elif length == 6:
            x = self.broken_three(array, opp)
            if x[0]:
                x.append(3)
                return x
            x = self.broken_three(array, colour)
            if x[0]:
                x.append(5)
                return x
        elif length == 7:
            x = self.three(array, opp)
            if x[0]:
                y = random.choice([x[1], x[2]])
                return [True, y, 4]
            x = self.three(array, colour)
            if x[0]:
                y = random.choice([x[1], x[2]])
                return [True, y, 6]
        return [False]

    def find_threats(self, length, colour, size, board):
        threat_list = {}
        # Read horizontally
        for row in range(size):
            for col in range(size - (length - 1)):
                array = board[row, col:col + length]
                i = self.threat_algo(array, colour, length)
                if i[0]:
                    threat_list.update({(row, col + i[1]): i[2]})

        # Read vertically
        for col in range(size):
            for row in range(size - (length - 1)):
                array = board[row:row + length, col]
                i = self.threat_algo(array, colour, length)
                if i[0]:
                    threat_list.update({(row + i[1], col): i[2]})

        # Read diagonally
        for row in range(size - (length - 1)):
            for col in range(size - (length - 1)):
                array = []
                for i in range(length):
                    array.append(board[i + row, i + col])
                # print(array)
                i = self.threat_algo(array, colour, length)
                if i[0]:
                    threat_list.update({(row + i[1], col + i[1]): i[2]})

                array = []
                for i in range(length):
                    array.append(board[i + row, col + length - 1 - i])
                # print(array)
                i = self.threat_algo(array, colour, length)
                if i[0]:
                    threat_list.update({(row + i[1], col + length - 1 - i[1]): i[2]})
        if len(threat_list.keys()) == 0:
            return False
        else:
            return threat_list

    #################
    ## Section (2) ##
    #################

    class node:
        def __init__(self, val):
            self.val = val
            self.children = []
            self.parent = False
            self.sol = None

        def set_child(self, child_node):
            self.children.append(child_node)

        def set_parent(self, parent_node):
            self.parent = parent_node

        def set_sol(self, node):
            self.sol = node

    def threat_space_search(self, board, root_node, p1_c, AI_c, size):
        found_sol = False
        sol_seq = []

        def store_seq(leaf_node):
            nonlocal sol_seq
            # print(leaf_node.val)
            sol_seq.insert(0, leaf_node.val)
            if leaf_node.parent:
                store_seq(leaf_node.parent)

        def make_threats(old_board, root_node, parent_node, depth):
            """
             Calling this func takes in a root node and initial board,
             loops through each square, place stone on square and check
             for any threats made. If a single threat is found, then
             update modified_board with the cost squares. Add that board
             to new_boards list. As long as winning sol is not found and
             there are some new boards, recursively call make_threats()
             until a sol is found or no more possible threats can be
             sequenced up.
            """
            nonlocal found_sol
            nonlocal sol_seq
            if depth < 3:
                new_boards = []
                for i in range(size):
                    for j in range(size):
                        if old_board[i][j] == empty:
                            modified_board = np.copy(old_board)
                            modified_board[i][j] = AI_c
                            bool_l = 0
                            bool_ll = 0
                            a = loop_board(size, 5, AI_c, modified_board, 0)
                            b = loop_board(size, 6, AI_c, modified_board, 0)
                            c = loop_board(size, 7, AI_c, modified_board, 0)
                            merged_threat_list = a + b + c
                            if len(merged_threat_list) == 1:
                                # print("Position: ",i,j)
                                # print("Threat List: ", merged_threat_list)
                                x = self.node([i, j])
                                x.set_parent(parent_node)
                                parent_node.set_child(x)
                                for each in merged_threat_list[0]:
                                    modified_board[each[0]][each[1]] = p1_c
                                new_boards.append([modified_board, x])
                            elif len(merged_threat_list) == 2:
                                # a secondary confirmation as a double
                                # threat may have been found but in fact
                                # the cost square of one interferes with the
                                # solution of the other

                                confirmed = False
                                confirmed2 = False
                                for t in merged_threat_list[0]:
                                    sol_board = modified_board.copy()
                                    sol_board[t[0], t[1]] = p1_c
                                for p in merged_threat_list[1]:
                                    if not confirmed:
                                        if sol_board[p[0], p[1]] == empty:
                                            sol_board1 = sol_board.copy()
                                            sol_board1[p[0], p[1]] = AI_c
                                            if loop_board(size, 5, AI_c, sol_board1, 1) or loop_board(size, 6, AI_c,
                                                                                                      sol_board1, 1):
                                                confirmed = True
                                if confirmed:
                                    for t in merged_threat_list[1]:  # assuming double-threat only
                                        sol_board = modified_board.copy()
                                        sol_board[t[0], t[1]] = p1_c
                                    for p in merged_threat_list[0]:
                                        if not confirmed2:
                                            if sol_board[p[0], p[1]] == empty:
                                                sol_board1 = sol_board.copy()
                                                sol_board1[p[0], p[1]] = AI_c
                                                if loop_board(size, 5, AI_c, sol_board1, 1) or loop_board(size, 6, AI_c,
                                                                                                          sol_board1,
                                                                                                          1):
                                                    confirmed2 = True

                                if confirmed and confirmed2:
                                    # print(merged_threat_list)
                                    # print('found a sol!')
                                    x = self.node([i, j])
                                    x.set_parent(parent_node)
                                    parent_node.set_child(x)
                                    root_node.set_sol(merged_threat_list)
                                    sol_seq = []
                                    store_seq(x)
                                    found_sol = True
                                    ##for each in merged_threat_list:
                                    ##    y = self.node(each)
                                    ##    y.set_parent(x)
                                    ##    x.set_child(y)

                if len(new_boards) != 0 and found_sol == False:
                    for each in new_boards:
                        # print('test')
                        make_threats(each[0], root_node, each[1], depth + 1)

        def loop_board(size, length, colour, board, spec):
            """
             Iterates through the board, returns a list of
             lists of cost_squares, each sub-list corresponding
             to a threat in the modified board.
             Note that it can be more efficient by just checking
             the vicinity of the position AI_c was placed at
            """
            threat_list = []
            for row in range(size):
                for col in range(size - (length - 1)):
                    array = board[row, col:col + length]
                    if spec == 0:
                        i = win_algo(array, colour, length)
                        if i[0]:
                            cost_squares = []
                            for each in i[1]:
                                cost_squares.append([row, col + each])
                            threat_list.append(cost_squares.copy())
                    else:
                        x = sol_algo(array, colour, length)
                        if x:
                            return x

            for col in range(size):
                for row in range(size - (length - 1)):
                    array = board[row:row + length, col]
                    if spec == 0:
                        i = win_algo(array, colour, length)
                        if i[0]:
                            cost_squares = []
                            for each in i[1]:
                                cost_squares.append([row + each, col])
                            threat_list.append(cost_squares.copy())
                    else:
                        x = sol_algo(array, colour, length)
                        if x:
                            return x

            for row in range(size - (length - 1)):
                for col in range(size - (length - 1)):
                    array = []
                    for i in range(length):
                        array.append(board[i + row, i + col])
                    # print(array)
                    if spec == 0:
                        i = win_algo(array, colour, length)
                        if i[0]:
                            cost_squares = []
                            for each in i[1]:
                                cost_squares.append([row + each, col + each])
                            threat_list.append(cost_squares.copy())
                    else:
                        x = sol_algo(array, colour, length)
                        if x:
                            return x

                    array = []
                    for i in range(length):
                        array.append(board[i + row, col + length - 1 - i])
                    # print(array)
                    if spec == 0:
                        i = win_algo(array, colour, length)
                        if i[0]:
                            cost_squares = []
                            for each in i[1]:
                                cost_squares.append([row + each, col + length - 1 - each])
                            threat_list.append(cost_squares.copy())
                    else:
                        x = sol_algo(array, colour, length)
                        if x:
                            return x
            if spec == 0:
                return threat_list
            else:
                return False

        def win_algo(array, colour, length):
            """
             Check if a threat formation is found, returns True and
             the cost squares if found
            """
            if length == 5:
                x = self.four(array, colour)
                if x[0]:
                    return [True, [x[1]]]
            elif length == 6:
                x = self.broken_three(array, colour)
                if x[0]:
                    return [True, [x[1]]]
            elif length == 7:
                x = self.three(array, colour)
                if x[0]:
                    return [True, x[1:]]
            return [False]

        def sol_algo(array, colour, length):
            if length == 5:
                x = self.five(array, colour)
                if x:
                    return x
            elif length == 6:
                x = self.straight_four(array, colour)
                if x:
                    return x
            return False

        make_threats(board, root_node, root_node, 0)
        if found_sol:
            return sol_seq
        else:
            return False

    #################
    ## Section (4) ##
    #################

    def maximise_own(self, board, p1_c, AI_c, turn):
        ## This is now considering when it is AI's first turn
        ## where we intend to place beside player's seed
        ## (Note: colour is player's colour, not AI's colour)
        if turn == 2:
            index = [np.where(board == p1_c)[0][0], np.where(board == p1_c)[1][0]]
            # If row index > column index i.e. bottom left triangle,
            # then place on top of opponent seed. Vice versa
            if index[0] > index[1]:
                return [index[0] - 1, index[1]]
            else:
                # else case includes when both indices are equal
                return [index[0] + 1, index[1]]
        ## This is where we consider connecting as many consecutive seeds
        ##  as possible
        else:
            score = {}
            for row, col in np.ndindex(board.shape):
                if board[row, col] == empty:
                    try:  # where we place our seed
                        score.update(self.check_surroundings(board, AI_c, row, col))
                    except IndexError:
                        pass
            ##print("Scores: ",score)
            v = list(score.values())
            k = list(score.keys())
            m = max(v)
            indices = [i for i, j in enumerate(v) if j == m]
            best_score = []
            for each in indices:
                if k[each][0] >= 0 and k[each][1] >= 0:
                    best_score.append(k[each])
            ##print("Best Placements: ",best_score)
            return random.choice(best_score)

    def check_surroundings(self, board, colour, row, col):
        ## Basically, given a possible position you can place your seed,
        ## calculate the score i.e. no. of consecutive seeds in all directions

        sub_score = 0  # how many consecutive seeds (directionless)
        score = 0
        empty_counter = 0

        def check_neighbour(original_row, original_col, row, col, direction, side, prev_is_empty):
            def num_to_dir(argument):
                def TLBR():
                    return [[row - 1, col - 1], [row + 1, col + 1]]

                def TRBL():
                    return [[row - 1, col + 1], [row + 1, col - 1]]

                def HORZ():
                    return [[row, col - 1], [row, col + 1]]

                def VERT():
                    return [[row - 1, col], [row + 1, col]]

                switcher = {
                    1: TLBR,
                    2: TRBL,
                    3: HORZ,
                    4: VERT,
                }
                func = switcher.get(argument)
                return func()

            try:
                nonlocal sub_score
                nonlocal score
                nonlocal empty_counter
                opp = self.get_opp[colour]

                # SIDE 0 (vs SIDE 1)
                if side == 0:
                    new_row = num_to_dir(direction)[0][0]
                    new_col = num_to_dir(direction)[0][1]
                elif side == 1:
                    new_row = num_to_dir(direction)[1][0]
                    new_col = num_to_dir(direction)[1][1]

                if new_row < 0:
                    new_row = 13
                elif new_col < 0:
                    new_col = 13
                ## if original_row == 3 and original_col == 4:
                ##     print("R: ",new_row, "C: ", new_col)
                if board[new_row, new_col] == colour:
                    if empty_counter == 1:
                        sub_score += 0.9
                    else:
                        sub_score += 1
                    check_neighbour(original_row, original_col, new_row, new_col, direction, side, False)
                elif board[new_row, new_col] == empty and empty_counter < 1:
                    ## We would only want to check up to 1 empty square beyond
                    empty_counter += 1
                    check_neighbour(original_row, original_col, new_row, new_col, direction, side, True)
                elif board[new_row, new_col] == empty and empty_counter == 1:
                    ## Flip side
                    if side == 0:
                        empty_counter = 0
                        check_neighbour(original_row, original_col, original_row, original_col, direction, 1, False)
                    else:
                        score += sub_score
                        sub_score = 0
                        empty_counter = 0
                elif board[new_row, new_col] == opp:
                    if prev_is_empty:
                        ## Flip side
                        if side == 0:
                            empty_counter = 0
                            check_neighbour(original_row, original_col, original_row, original_col, direction, 1, False)
                        else:
                            score += sub_score
                            sub_score = 0
                            empty_counter = 0
                    else:
                        sub_score = 0
                        empty_counter = 0
            except IndexError:
                if side == 0:
                    # Flip side
                    empty_counter = 0
                    check_interference(original_row, original_col, original_row, original_col, direction, 1)
                else:
                    score += sub_score
                    sub_score = 0
                    empty_counter = 0

        def check_interference(original_row, original_col, row, col, direction, side):
            def num_to_dir(argument):
                def TLBR():
                    return [[row - 1, col - 1], [row + 1, col + 1]]

                def TRBL():
                    return [[row - 1, col + 1], [row + 1, col - 1]]

                def HORZ():
                    return [[row, col - 1], [row, col + 1]]

                def VERT():
                    return [[row - 1, col], [row + 1, col]]

                switcher = {
                    1: TLBR,
                    2: TRBL,
                    3: HORZ,
                    4: VERT,
                }
                func = switcher.get(argument)
                return func()

            try:
                nonlocal score
                nonlocal sub_score
                nonlocal empty_counter

                opp = self.get_opp[colour]
                    # SIDE 0 (vs SIDE 1)
                if side == 0:
                    new_row = num_to_dir(direction)[0][0]
                    new_col = num_to_dir(direction)[0][1]
                elif side == 1:
                    new_row = num_to_dir(direction)[1][0]
                    new_col = num_to_dir(direction)[1][1]
                if new_row < 0:
                    new_row = 13
                elif new_col < 0:
                    new_col = 13

                ## if original_row == 3 and original_col == 0:
                ##     print("R: ",new_row, "C: ",new_col) 
                if board[new_row, new_col] == opp:
                    if empty_counter == 1:
                        sub_score += 0.9
                    else:
                        sub_score += 1
                    check_interference(original_row, original_col, new_row, new_col, direction, side)
                elif board[new_row, new_col] == empty and empty_counter < 1:
                    empty_counter += 1
                    check_interference(original_row, original_col, new_row, new_col, direction, side)
                elif board[new_row, new_col] == colour:
                    ## If you hit into your own seed, it means you're
                    ## already blocking opponent, if any. So ignore
                    sub_score = 0
                    empty_counter = 0
                else:
                    if side == 0:
                        # Flip side
                        empty_counter = 0
                        check_interference(original_row, original_col, original_row, original_col, direction, 1)
                    else:
                        score += sub_score
                        sub_score = 0
                        empty_counter = 0
            except IndexError:
                if side == 0:
                    # Flip side
                    empty_counter = 0
                    check_interference(original_row, original_col, original_row, original_col, direction, 1)
                else:
                    score += sub_score
                    sub_score = 0
                    empty_counter = 0

        ## Check for all directions individually
        for i in range(4):
            check_neighbour(row, col, row, col, i + 1, 0, False)

            ## If my pieces are less than opponent
            ## => I gain advantage by interfering,
            ## more so than I lose out from being interfered.
            ## Hence we need to consider this special case and add it to score

            check_interference(row, col, row, col, i + 1, 0)

        return {(row, col): score}


game = Board(board, AI, (1, 2))
game.prompt_input()
