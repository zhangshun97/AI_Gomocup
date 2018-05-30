## Development log

### Shun Zhang
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

(2018/05/30 20:26:01)
- Points 1.0
- TODO: deep search and pruning

### Donghao Li

### Pingxuan Huang

---
## pbrain-pyrandom

#### A Python Piskvork template

**pbrain-pyrandom** is the technical core of a "brain" (AI) for [Piskvork gomoku manager](http://petr.lastovicka.sweb.cz/piskvork.zip)
used in [Gomocup AI tournament](http://gomocup.org), written in Python.

The code is basically the "Python copy" of [C++ template](http://petr.lastovicka.sweb.cz/skel_cpp.zip) written by [Petr Lastovicka](http://petr.lastovicka.sweb.cz/indexEN.html).
This README is also partially copy of the C++ template's README.

#### Prerequisites and compilation
The Piskvork manager is a Win32 application and currently supports only Win32 compatible .exe files (furthermore whose name starts with pbrain- prefix).
There are several ways how to create .exe from Python files.

Here I present the approach using [PyInstaller](http://pyinstaller.org) and Windows command line:

1. Install Windows (or [Wine](https://www.winehq.org/) for Linux, originally the project was created and tested on Ubuntu 16.04 using Wine)
2. Install [Python](http://www.python.org) (the code and also following instructions were tested with versions 2.7 and 3.6).
3. Install [pywin32](https://sourceforge.net/projects/pywin32) Python package: `pip.exe install pypiwin32` (if not present "by default")
4. Install [PyInstaller](https://www.pyinstaller.org/): `pip.exe install pyinstaller`

To compile the example, use the following command line command:
```
cd C:\path\where\the\files\were\saved
pyinstaller.exe example.py pisqpipe.py --name pbrain-pyrandom.exe --onefile
```

Note: the executables `pip.exe` and `pyinstaller.exe` might need full path, in my case I used `C:\Python27\Scripts\pip.exe` and `C:\Python27\Scripts\pyinstaller.exe`.

#### How to create your own AI
Replace file example.py with your own algorithm. Please don't change file pisqpipe.py, because it contains communication between your AI and the game manager and it might be changed in future protocol versions. 
More information about the protocol and tournament rules can be found at [Gomocup websites](http://gomocup.org)
