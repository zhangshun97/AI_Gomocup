## Monte-Carlo Tree Search

This is a Python implementation of paper [Effective Monte-Carlo tree search strategies for Gomoku AI](https://pdfs.semanticscholar.org/ab9c/5db14c2194de48779cf3e968f6656d9a3a45.pdf).

MCTS algorithm requires a great number of simulations to converge. When there is limited computation resource and time, the MCTS algorithm often returns a bad result of simulation.

- Quick start: `python3 mcts3.0.py `
- Attributions:
  - `--time-limit`
  - `--board-size`
  - `--n-in-line`
  - `--detail`
  - ...
- more attribution details refer to `python3 mcts3.0.py --help`

**Note that** this code excludes the module to end the game when some one wins, so please check it yourself!

## Development log

(2018/05/25 20:49:06)
- Add `class Board`:
	- usage: `your_board = Board(input_board)`
	- Note that this gives you a **deep copy** of `input_board`, which is very flexible while coding
	- get all the empty places: `your_board.availables`, which is a `set`
	- check whether `(x, y)` is free to take: `your_board.is_free(x, y)`
	- update the your_board after a step `(x, y)`: `your_board.update(player, (x, y))`
		- Note that `player` is the one takes move `(x, y)`
		- Note that this function also returns 1 or 0, 
		  1 means player wins after taking this move, 0 means nothing special happens
		- So I suggest you to do as follows:
		```
		if your_board.update(player, (x, y)):
			winner = your_board.winner	
		```
	- more details please refer to *example.py*

(2018/05/28 23:05:00)
- MCTS 2.0 finished, which is the basic form of MCTS, but still powerful on small board like 8x8.
- Add `class MCTS`:
    - usage:
    ```
    MCTS_AI = MCTS(board,
                   players_in_turn=[1, 2],  # brain is 1
                   n_in_line=5,
                   confidence=2,
                   time_limit=10,
                   max_simulation=5,
                   max_simulation_one_play=50)
    move = MCTS_AI.get_action()
    ```
- Add `class Node`:
    - usage:
    ```
    your_node = Node(None,
                     players_in_turn=players_in_turn,  # here is a reverse, because root is your opponent
                     num_child=len(self.MCTSboard.availables),
                     possible_moves_for_child=self.MCTSboard.availables,
                     possible_moves_for_expansion=self.MCTSboard.availables)
    ```
    - this class is mainly built for the MCTS tree

(2018/05/29 17:15:00)
- MCTS 3.0, neighbor search
- TODO: update the simulations of player 2, which should also stick to the move which leads to win, 1-lose.
