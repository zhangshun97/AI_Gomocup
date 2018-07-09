# Hi, Gomoku!

This project is a competitive project in course [Introduction to Artificial Intelligence](http://www.sdspeople.fudan.edu.cn/zywei/DATA130008/index.html).

The Gomoku AIs are based on the Gomocup standard and you can create your own `AI.exe` through `pisqpipe`, the materials and document are [here](https://github.com/zhangshun97/AI_Gomocup/tree/master/pisqpipe).

- The rule is: Free Style

## Our team

We have three amazing guys here, [Shun Zhang](https://github.com/zhangshun97), [Donghao Li](https://github.com/Lidonghao1996) and [Pingxuan Huang](https://github.com/Explorerhpx).

- The Genetic Algorithm is supported by Pingxuan.
- The VCX Algorithm is supported by Donghao.
- The MCTS Algorithm and Minimax Algorithm are supported by me.
- The report is [here](https://github.com/zhangshun97/AI_Gomocup/blob/master/report.pdf).

**Note that** all the algorithms listed below can be packed into a win32 exe (less than 20m with bumpy version 1.13.1), which is tested by us. We think the `pisqpipe` platform is far from perfect and there are too many unknown or stupid errors. So we just provide the terminal APIs. You can play with our AIs through command `$python AI-name.py`(more details please refer to relating page). Still, one can easily pack the AIs into win32 exe with the 'help' of [pisqpipe](https://github.com/zhangshun97/AI_Gomocup/tree/master/pisqpipe).

## Realized Algorithms

- [Monte-Carlo Tree Search](https://github.com/zhangshun97/AI_Gomocup/tree/master/mcts)
- [Genetic Algorithm](https://github.com/zhangshun97/AI_Gomocup/tree/master/GA)
- [Minimax Search](https://github.com/zhangshun97/AI_Gomocup/tree/master/final)
  - VCX
  - Alpha-beta pruning
  - Zobrist transition table
  - dinamic updating with pattern score

*More detailed document please refer to relating page.*

Also, there is a python version of [Threat Space Search](https://github.com/zhangshun97/AI_Gomocup/tree/master/TSS), which is designed by [Xavier Wee](https://github.com/xavierwwj). However, we found it too slow for a board as big as `20 x 20`. Optimizations are required.