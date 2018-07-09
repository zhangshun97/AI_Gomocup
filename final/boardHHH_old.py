# zs: 我在这里使用了字典进行打分，完全取代了 evaluate-point 的方式

import numpy as np
from role import role
from zobrist import Zobrist
from config import Config
from score import score
from pointCache import pointCache
import time

R = role()
config = Config()
np.set_printoptions(precision=0)

# 冲四的分其实肯定比活三高，但是如果这样的话容易形成盲目冲四的问题，所以如果发现电脑有无意义的冲四，则将分数降低到和活三一样
# 而对于冲四活三这种杀棋，则将分数提高。


def fixScore(type_score):
    # 这里的 type_score 是一个对应 pattern 的得分
    if score['BLOCKED_FOUR'] <= type_score < score['FOUR']:

        if score['BLOCKED_FOUR'] <= type_score < (score['BLOCKED_FOUR'] + score['THREE']):
            # 单独冲四意义不大
            return score['THREE']
        elif score['BLOCKED_FOUR'] + score['THREE'] <= type_score < score['BLOCKED_FOUR'] * 2:
            # 冲四活三，比双三分数高，相当于自己形成活四
            return score['FOUR']
        else:
            # 双冲四，比活四分数高
            return score['FOUR'] * 2

    return type_score


def fixFour(type_score):
    if score['BLOCKED_FOUR'] <= type_score < score['BLOCKED_FOUR'] + score['THREE']:
        return score['THREE'] - 1

    if score['BLOCKED_THREE'] <= type_score < score['THREE']:
        return score['TWO'] - 1

    if type_score == score['TWO']:
        return type_score + 10

    return type_score


class Board:

    def __init__(self, board):
        self.board = np.array(board).copy()
        self.height = len(board)
        self.width = len(board[0])
        assert self.width == self.height, "board is not square"
        self.size = self.width

        self.scoreCache = np.zeros([2, 4, self.height, self.width])

        self.genCache = {}
        # onlyThree
        self.gen3Cache = {}

        self.steps = []
        self.allSteps = []

        self.zobrist = Zobrist(self.size)
        self.zobrist.init()  # remember to re-initialize
        self._last = [False, False]  # record the last step

        # store the scores
        self.AIScore = np.zeros([self.height, self.width])
        self.oppScore = np.zeros([self.height, self.width])

        # 用来控制时间，以免超时
        self.startTime = None
        # 用来作为 self.hasNeighbor 的缓存
        self.neighborCache = {}

        # point score for player X in direction Y (0, 1, 2, 3) for '--', '|', '\', '/'
        #     self.pointCache.get(self.patternCache[X][position[0]][position[1]][Y], 0)[X-1]
        # PAY ATTENTION !!! its ==> [X - 1] <== !!!
        # self.patternCache has size (3, 20, 20, 4)
        self.patternCache = [
            [],
            [[[0, 0, 0, 0] for _ in range(self.width)] for _ in range(self.height)],
            [[[0, 0, 0, 0] for _ in range(self.width)] for _ in range(self.height)],
        ]
        # self.patternCache = np.zeros([3, 20, 20, 4], dtype='int64')

        self.initScore()
        # TODO: check the usage of this table
        # self.statisticTable = np.zeros([self.height, self.width])
        # print(self.patternCache[1])

        # LDH niu pi
        self.attackRate = config.attackRate

    def initScore(self):
        # TODO: check if this is equivalent to the p.item thing
        self.attack = {}
        self.score = {}
        self.role = {}
        self.scoreHum = {}
        self.scoreCom = {}

        # hhh, 这里用了外接字典，可以直接模式匹配 int => 分数，取代了 evaluate-point 函数
        # with open('pointCache.txt', 'r') as f:
        #     a = f.read()
        #     self.pointCache = eval(a)
        self.pointCache = pointCache

        # 初始化 pattern 分数，主要用于应对靠近边上的点，即天然有墙堵着
        for i in range(self.height):
            for j in range(self.width):
                if 5 <= i < self.height - 5 and 5 <= j < self.width - 5:
                    continue
                # --
                for dd in range(1, 6):
                    y = j - dd
                    if y < 0:
                        self.patternCache[R.AI][i][j][0] += R.opp * R.mm ** (5 + dd)
                        self.patternCache[R.opp][i][j][0] += R.AI * R.mm ** (5 + dd)
                        break
                for dd in range(1, 6):
                    y = j + dd
                    if y >= self.width:
                        self.patternCache[R.AI][i][j][0] += R.opp * R.mm ** (5 - dd)
                        self.patternCache[R.opp][i][j][0] += R.AI * R.mm ** (5 - dd)
                        break
                # |
                for dd in range(1, 6):
                    x = i - dd
                    if x < 0:
                        self.patternCache[R.AI][i][j][1] += R.opp * R.mm ** (5 + dd)
                        self.patternCache[R.opp][i][j][1] += R.AI * R.mm ** (5 + dd)
                        break
                for dd in range(1, 6):
                    x = i + dd
                    if x >= self.height:
                        self.patternCache[R.AI][i][j][1] += R.opp * R.mm ** (5 - dd)
                        self.patternCache[R.opp][i][j][1] += R.AI * R.mm ** (5 - dd)
                        break
                # \
                for dd in range(1, 6):
                    x, y = i - dd, j - dd
                    if x < 0 or y < 0:
                        self.patternCache[R.AI][i][j][2] += R.opp * R.mm ** (5 + dd)
                        self.patternCache[R.opp][i][j][2] += R.AI * R.mm ** (5 + dd)
                        break
                for dd in range(1, 6):
                    x, y = i + dd, j + dd
                    if x >= self.height or y >= self.width:
                        self.patternCache[R.AI][i][j][2] += R.opp * R.mm ** (5 - dd)
                        self.patternCache[R.opp][i][j][2] += R.AI * R.mm ** (5 - dd)
                        break
                # /
                for dd in range(1, 6):
                    x, y = i - dd, j + dd
                    if x < 0 or y >= self.width:
                        self.patternCache[R.AI][i][j][3] += R.opp * R.mm ** (5 + dd)
                        self.patternCache[R.opp][i][j][3] += R.AI * R.mm ** (5 + dd)
                        break
                for dd in range(1, 6):
                    x, y = i + dd, j - dd
                    if x >= self.height or y < 0:
                        self.patternCache[R.AI][i][j][3] += R.opp * R.mm ** (5 - dd)
                        self.patternCache[R.opp][i][j][3] += R.AI * R.mm ** (5 - dd)
                        break

        # 注意初始化分数的更新顺序！（hhh, 好像无所谓了）
        for i in range(self.height):
            for j in range(self.width):
                # get score for both players
                if self.board[i, j] != R.empty:
                    self.updateScore((i, j))
                    self.allSteps.append((i, j))

    # 只更新一个点附近的分数
    # 参见 evaluate 中的代码，为了优化性能，在更新分数的时候可以指定只更新某一个方向的分数
    def updateScore(self, position, remove=False):
        # 更新 pattern, 再更新分数
        if_remove = -1 if remove else 1
        radius = 6
        player = self.board[position[0]][position[1]]
        # 先更新自己的
        # if player == R.AI:
        #     self.oppScore[position[0]][position[1]] = 0
        # elif player == R.opp:
        #     self.AIScore[position[0]][position[1]] = 0
        updatedPositions = []
        # update no matter empty or not
        # --
        for dd in range(0, radius):
            x, y = position[0], position[1] - dd
            if y < 0:
                break
            self.patternCache[R.AI][x][y][0] += player * R.mm ** (5 - dd) * if_remove
            self.patternCache[R.opp][x][y][0] += player * R.mm ** (5 - dd) * if_remove
            updatedPositions.append((x, y))
        for dd in range(1, radius):
            x, y = position[0], position[1] + dd
            if y >= self.width:
                break
            self.patternCache[R.AI][x][y][0] += player * R.mm ** (5 + dd) * if_remove
            self.patternCache[R.opp][x][y][0] += player * R.mm ** (5 + dd) * if_remove
            updatedPositions.append((x, y))
        # |
        for dd in range(0, radius):
            x, y = position[0] - dd, position[1]
            if x < 0:
                break
            self.patternCache[R.AI][x][y][1] += player * R.mm ** (5 - dd) * if_remove
            self.patternCache[R.opp][x][y][1] += player * R.mm ** (5 - dd) * if_remove
            updatedPositions.append((x, y))
        for dd in range(1, radius):
            x, y = position[0] + dd, position[1]
            if x >= self.height:
                break
            self.patternCache[R.AI][x][y][1] += player * R.mm ** (5 + dd) * if_remove
            self.patternCache[R.opp][x][y][1] += player * R.mm ** (5 + dd) * if_remove
            updatedPositions.append((x, y))
        # \
        for dd in range(0, radius):
            x, y = position[0] - dd, position[1] - dd
            if x < 0 or y < 0:
                break
            self.patternCache[R.AI][x][y][2] += player * R.mm ** (5 - dd) * if_remove
            self.patternCache[R.opp][x][y][2] += player * R.mm ** (5 - dd) * if_remove
            updatedPositions.append((x, y))
        for dd in range(1, radius):
            x, y = position[0] + dd, position[1] + dd
            if x >= self.height or y >= self.width:
                break
            self.patternCache[R.AI][x][y][2] += player * R.mm ** (5 + dd) * if_remove
            self.patternCache[R.opp][x][y][2] += player * R.mm ** (5 + dd) * if_remove
            updatedPositions.append((x, y))
        # /
        for dd in range(0, radius):
            x, y = position[0] - dd, position[1] + dd
            if x < 0 or y >= self.width:
                break
            self.patternCache[R.AI][x][y][3] += player * R.mm ** (5 - dd) * if_remove
            self.patternCache[R.opp][x][y][3] += player * R.mm ** (5 - dd) * if_remove
            updatedPositions.append((x, y))
        for dd in range(1, radius):
            x, y = position[0] + dd, position[1] - dd
            if x >= self.height or y < 0:
                break
            self.patternCache[R.AI][x][y][3] += player * R.mm ** (5 + dd) * if_remove
            self.patternCache[R.opp][x][y][3] += player * R.mm ** (5 + dd) * if_remove
            updatedPositions.append((x, y))
        # 一次性更新所有需要更新分数的点

        for p in updatedPositions:
            self.AIScore[p] = self.scorePoint(p, R.AI)
            self.oppScore[p] = self.scorePoint(p, R.opp)

    def scorePoint(self, position, player):
        result = 0
        pattern = self.patternCache[player][position[0]][position[1]][0]
        result += self.pointCache[pattern][player - 1]
        pattern = self.patternCache[player][position[0]][position[1]][1]
        result += self.pointCache[pattern][player - 1]
        pattern = self.patternCache[player][position[0]][position[1]][2]
        result += self.pointCache[pattern][player - 1]
        pattern = self.patternCache[player][position[0]][position[1]][3]
        result += self.pointCache[pattern][player - 1]
        return result

    # get next move
    def put(self, position, player, record):
        if config.debug:
            print(player, 'put [', position, ']')
        self.board[position] = player
        self.zobrist.go(position, player)
        if record:
            # self.steps.append(position)
            self.updateScore(position)
            self.allSteps.append(position)
            # print(position, '=====', self.oppScore[position])

    # the last step
    def last(self, player):
        for i in range(len(self.allSteps) - 1):
            p = self.allSteps[-i]
            if self.board[p] == player:
                return p
        return False

    def remove(self, position):
        r = self.board[position]
        if config.debug:
            print(r, 'remove [', position, ']')
        self.zobrist.go(position, r)
        self.updateScore(position, remove=True)
        self.allSteps.pop()
        self.board[position] = R.empty

    # TODO: 悔棋
    def back(self):
        if len(self.steps) < 2:
            return
        s = self.steps.pop()
        self.zobrist.go(s, self.board[s])
        self.board[s] = R.empty
        self.updateScore(s)
        self.allSteps.pop()
        s = self.steps.pop()
        self.zobrist.go(s, self.board[s])
        self.board[s] = R.empty
        self.updateScore(s)
        self.allSteps.pop()

    def logSteps(self):
        # TODO:
        pass

    # 棋面估分
    # 这里只算当前分，而不是在空位下一步之后的分
    def evaluate(self):
        # 这里都是用正整数初始化的，所以初始值是0
        self.AIMaxScore = 0
        self.oppMaxScore = 0

        # 遍历出最高分，开销不大
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i, j] == R.AI:
                    self.AIMaxScore = max(self.AIScore[i, j], self.AIMaxScore)
                elif self.board[i, j] == R.opp:
                    self.oppMaxScore = max(self.oppScore[i, j], self.oppMaxScore)

        # 有冲四延伸了，不需要专门处理冲四活三
        # 不过这里做了这一步，可以减少电脑胡乱冲四的毛病
        self.AIMaxScore = fixScore(self.AIMaxScore)
        self.oppMaxScore = fixScore(self.oppMaxScore)
        # TODO: check if 1/-1 is needed
        # result = (1 if player == R.AI else -1) * (self.AIMaxScore - self.oppMaxScore)
        result = self.AIMaxScore - self.oppMaxScore * self.attackRate

        return result

    def log(self):
        # TODO:
        pass

    # 启发函数
    #
    # 变量starBread的用途是用来进行米子计算
    # 所谓米子计算，只是，如果第一步尝试了一个位置A，那么接下来尝试的位置有两种情况：
    # 1: 大于等于活三的位置
    # 2: 在A的米子位置上
    # 注意只有对小于活三的棋才进行starSpread优化

    # gen 函数的排序是非常重要的，因为好的排序能极大提升AB剪枝的效率。
    # 而对结果的排序，是要根据role来的
    def cache(self, result, onlyThree=False):
        if not config.cache:
            return
        if onlyThree:
            self.gen3Cache[self.zobrist.boardHashing[0]] = result
        else:
            self.genCache[self.zobrist.boardHashing[0]] = result

    def getCache(self, onlyThree=False):
        if not config.cache:
            return
        if onlyThree:
            result = self.gen3Cache.get(self.zobrist.boardHashing[0], None)
        else:
            result = self.genCache.get(self.zobrist.boardHashing[0], None)
        return result

    def gen(self, player, onlyThrees=False, starSpread=False):
        r = self.getCache(onlyThrees)
        if r:
            return r
        # if config.debugGen:
        #     print("====== GEN for {} ======".format(player))
        fives = []
        AIfours = []
        oppfours = []
        AIblockedfours = []
        oppblockedfours = []
        AItwothrees = []
        opptwothrees = []
        AIthrees = []
        oppthrees = []
        AItwos = []
        opptwos = []
        neighbors = []

        # 找到双方的最后进攻点
        # lastPoint1 = None
        # lastPoint2 = None

        # 默认情况下 我们遍历整个棋盘。但是在开启star模式下，我们遍历的范围就会小很多
        # 只需要遍历以两个点为中心正方形。
        # 注意除非专门处理重叠区域，否则不要把两个正方形分开算，因为一般情况下这两个正方形会有相当大的重叠面积，别重复计算了
        startI = 0
        startJ = 0
        endI = self.size - 1
        endJ = self.size - 1
        # TODO: 双星搜索有毛病
        # if len(self.allSteps) >= 2 and starSpread and config.star:
        #
        #     i = len(self.allSteps) - 1
        #     while not lastPoint1 and i >= 0:
        #         p = self.allSteps[i]
        #         if self.role.get(p, None) != player and self.attack.get(p, None) != player:
        #             lastPoint1 = p
        #         i -= 2
        #
        #     if not lastPoint1:
        #         if self.role.get(self.allSteps[0], None) != player:
        #             lastPoint1 = self.allSteps[0]
        #         else:
        #             lastPoint1 = self.allSteps[1]
        #     i = len(self.allSteps) - 2
        #     while not lastPoint2 and i >= 0:
        #         p = self.allSteps[i]
        #         if self.attack.get(p, None):
        #             lastPoint2 = p
        #         i -= 2
        #
        #     if not lastPoint2:
        #         if self.role.get(self.allSteps[0], None) == player:
        #             lastPoint2 = self.allSteps[0]
        #         else:
        #             lastPoint2 = self.allSteps[1]
        #
        #     # 根据双方最后的进攻点周围展开搜索
        #     if config.debugGen:
        #         print("1 attack point: {}, 2 attack point: {}".format(lastPoint1, lastPoint2))
        #
        #     startI = min(lastPoint1[0] - 5, lastPoint2[0] - 5)
        #     startJ = min(lastPoint1[1] - 5, lastPoint2[1] - 5)
        #     startI = max(0, startI)
        #     startJ = max(0, startJ)
        #     endI = max(lastPoint1[0] + 5, lastPoint2[0] + 5)
        #     endJ = max(lastPoint1[1] + 5, lastPoint2[1] + 5)
        #     endI = min(self.size - 1, endI)
        #     endJ = min(self.size - 1, endJ)

        for i in range(startI, endI + 1):
            for j in range(startJ, endJ + 1):
                p = (i, j)
                if self.board[i][j] == R.empty:
                    neighbor = (2, 2)  # 两步以内有 2 个子, restricted by calculation capability
                    if len(self.allSteps) <= 2:
                        neighbor = (1, 1)
                    if self.hasNeighbor((i, j), neighbor[0], neighbor[1]):
                        scoreOpp = self.oppScore[i][j]
                        self.scoreHum[p] = scoreOpp
                        scoreAI = self.AIScore[i][j]
                        self.scoreCom[p] = scoreAI
                        maxScore = max(scoreOpp, scoreAI)
                        self.score[p] = maxScore
                        self.role[p] = player
                        # 标记当前点是为了进攻还是为了防守，后面会用到
                        if scoreAI > scoreOpp:
                            self.attack[p] = R.AI  # attack point
                        else:
                            self.attack[p] = R.opp  # defend point

                        # 双星延伸，以提升性能
                        # 思路：每次下的子，只可能是自己进攻，或者防守对面（也就是对面进攻点）
                        # 我们假定任何时候，绝大多数情况下进攻的路线都可以按次序连城一条折线，那么每次每一个子，一定都是在上一个己方棋子的八个方向之一。
                        # 因为既可能自己进攻，也可能防守对面，所以是最后两个子的米子方向上
                        # 那么极少数情况，进攻路线无法连成一条折线呢?很简单，我们对前双方两步不作star限制就好，这样可以 兼容一条折线中间伸出一段的情况
                        # TODO: 双星搜索还不稳定
                        # if lastPoint1 and lastPoint2 and config.star:
                        #     # 距离必须在5步以内
                        #     if (np.abs(i - lastPoint1[0]) > 5 or np.abs(j - lastPoint1[1]) > 5) and \
                        #             (np.abs(i - lastPoint2[0]) > 5 or np.abs(j - lastPoint2[1]) > 5):
                        #         continue
                        #     # 必须在米子方向上
                        #     if maxScore >= score['FIVE'] or \
                        #             (i == lastPoint1[0] or j == lastPoint1[1] or (
                        #                     np.abs(i - lastPoint1[0]) == np.abs(j - lastPoint1[1]))) \
                        #             or (i == lastPoint2[0] or j == lastPoint2[1] or (
                        #             np.abs(i - lastPoint2[0]) == np.abs(j - lastPoint2[1]))):
                        #         pass
                        #     else:
                        #         continue

                        if scoreAI >= scoreOpp:
                            if scoreAI >= score['FIVE']:
                                # 先看电脑能不能连成 5
                                return [p]
                            elif scoreAI >= score['FOUR']:
                                AIfours.append(p)
                            elif scoreAI >= score['BLOCKED_FOUR']:
                                AIblockedfours.append(p)
                            elif scoreAI >= 2 * score['THREE']:  # 能成双三也很强
                                AItwothrees.append(p)
                            elif scoreAI >= score['THREE']:
                                AIthrees.append(p)
                            elif scoreAI >= score['TWO']:
                                AItwos.append(p)
                            else:
                                neighbors.append(p)
                        else:
                            if scoreOpp >= score['FIVE']:
                                # 再看玩家能不能连成 5
                                # 别急着返回，因为遍历还没完成，说不定电脑自己能成五
                                fives.append(p)
                            elif scoreOpp >= score['FOUR']:
                                oppfours.append(p)
                            elif scoreOpp >= score['BLOCKED_FOUR']:
                                oppblockedfours.append(p)
                            elif scoreOpp >= 2 * score['THREE']:
                                opptwothrees.append(p)
                            elif scoreOpp >= score['THREE']:
                                oppthrees.append(p)
                            elif scoreOpp >= score['TWO']:
                                opptwos.append(p)
                            else:
                                neighbors.append(p)
        # if config.debugGen:
        #     print(
        #         'fives', fives, '\n',
        #         'AIfours', AIfours, '\n',
        #         'AI23', AItwothrees, '\n',
        #         'AI4s', AIblockedfours, '\n',
        #         'AI3s', AIthrees, '\n',
        #     )
        #     print(
        #         'oppfours', oppfours, '\n',
        #         'opp23s', opptwothrees, '\n',
        #         'opp4s', oppblockedfours, '\n',
        #         'opp3s', oppthrees, '\n',
        #     )
        # 如果成五，是必杀棋，直接返回
        if fives:
            self.cache(fives, onlyThrees)
            return fives
        # 自己能活四，则直接活四，不考虑冲四
        if player == R.AI and AIfours:
            self.cache(fives, onlyThrees)
            return AIfours
        if player == R.opp and oppfours:
            self.cache(fives, onlyThrees)
            return oppfours

        # 对面有活四冲四，自己冲四都没，则只考虑对面活四 （此时对面冲四就不用考虑了)
        if player == R.AI and oppfours and not AIblockedfours:
            self.cache(fives, onlyThrees)
            return oppfours
        if player == R.opp and AIfours and not oppblockedfours:
            self.cache(fives, onlyThrees)
            return AIfours

        # 对面有活四自己有冲四，则都考虑下
        fours = AIfours + oppfours if player == R.AI else oppfours + AIfours
        blockedfours = AIblockedfours + oppblockedfours if player == R.opp else oppblockedfours + AIblockedfours
        if fours:
            self.cache(fives, onlyThrees)
            return fours + blockedfours

        result = []
        if player == R.AI:
            result = AItwothrees + opptwothrees \
                     + AIblockedfours \
                     + oppblockedfours \
                     + AIthrees \
                     + oppthrees
        if player == R.opp:
            result = opptwothrees + AItwothrees \
                     + oppblockedfours \
                     + AIblockedfours \
                     + oppthrees \
                     + AIthrees

        # TODO: 限制长度，讲道理来说这里最好是能全搜
        if len(result) > config.countLimit:
            result = result[:config.countLimit]

        # 双三很特殊，因为能形成双三的不一定比一个活三强
        if AItwothrees or opptwothrees:
            self.cache(fives, onlyThrees)
            return result

        # 只返回大于等于活三的棋
        if onlyThrees:
            self.cache(fives, onlyThrees)
            return result

        if player == R.AI:
            twos = AItwos + opptwos
        else:
            twos = opptwos + AItwos

        # 从大到小排序
        twos.sort(key=lambda x: self.score.get(x, 0), reverse=True)
        _toExtend = twos if twos else neighbors
        result.extend(_toExtend)

        # 这种分数低的，就不用全部计算了
        if len(result) > config.countLimit:
            self.cache(fives, onlyThrees)
            return result[:config.countLimit]
        self.cache(fives, onlyThrees)
        return result

    def hasNeighbor(self, position, distance, count):
        # 3309    0.013    0.000    0.026    0.000 board.py:545(hasNeighbor) 11 10 3 7
        #    520517    1.958    0.000    3.835    0.000 board.py:544(hasNeighbor)
        # this function will check the exact surrounding of the position
        # return TRUE is there are >= count neighbors
        # for example: distance = 1
        #  XXX
        #  XOX
        #  XXX
        # all the 'X's are neighbors of 'O'
        if self.board[position] == R.empty:
            startX = max(position[0] - distance, 0)
            endX = min(position[0] + distance + 1, self.size)
            startY = max(position[1] - distance, 0)
            endY = min(position[1] + distance + 1, self.size)
            if np.sum(self.board[startX:endX, startY:endY] != R.empty) >= count:
                return True
            else:
                return False
        else:
            startX = max(position[0] - distance, 0)
            endX = min(position[0] + distance + 1, self.size)
            startY = max(position[1] - distance, 0)
            endY = min(position[1] + distance + 1, self.size)
            if np.sum(self.board[startX:endX, startY:endY] != R.empty) >= count + 1:
                return True
            else:
                return False

    def get_value(self, player, position, deep, alpha, beta):
        # 这个函数得到的值应该是 player 下了这个点之后的 reward
        # 所以这里还没下
        # 先看看能不能 win
        if self.win(player, position):
            # if config.debugAB:
            #     print("{} win found!".format(player))
                # print(self.board)
            return self.MAX if player == R.AI else self.MIN

        # 然后 player 下这个子
        self.put(position, player, True)
        # if config.debugAB:
        #     print("{} takes : {}".format(player, position))

        # time out
        if time.clock() - self.startTime > config.timeLimit:
            self.remove(position)
            return 0.5

        # if is leaf node
        if deep <= 0:
            r = self.evaluate()
            # if config.debugAB:
            #     print("{} Score -------> {}".format(player, r))
            # 记得撤掉之前 player 下的子
            if self.win(R.get_opponent(player)):
                self.remove(position)
                if player == R.AI:
                    return self.MIN
                elif player == R.opp:
                    return self.MAX
            self.remove(position)
            return r

        result = 0
        # MIN
        if player == R.AI:
            result = self.min_value(R.opp, deep - 1, alpha, beta)
        # MAX
        if player == R.opp:
            result = self.max_value(R.AI, deep - 1, alpha, beta)

        # 记得撤掉之前 player 下的子
        self.remove(position)
        # if config.debugAB:
        #     print("{} Score -------> {} at {}".format(player, result, position))
        # 然后返回
        return result

    def max_value(self, player, deep, alpha, beta):
        v = self.MIN
        # get successors
        successors = self.gen(player, starSpread=False)
        # if config.debugAB:
        #     print("MAX({}) node successors: {} =====> Deep: {}".format(player, successors, deep))
        for point in successors:
            v = max(v, self.get_value(player, point, deep, alpha, beta))
            # pruning
            if v >= beta:
                return v
            alpha = max(v, alpha)
        return v

    def min_value(self, player, deep, alpha, beta):
        v = self.MAX
        # get successors
        successors = self.gen(player, starSpread=False)
        # if config.debugAB:
        #     print("MIN({}) node successors: {} =====> Deep: {}".format(player, successors, deep))
        for point in successors:
            v = min(v, self.get_value(player, point, deep, alpha, beta))
            # pruning
            if v <= alpha:
                return v
            beta = min(v, beta)
        return v

    def negamax(self, deep):
        self.MIN = -1 * score['FIVE'] * 10
        self.MAX = score['FIVE'] * 10
        bestPoints = []
        best = self.MIN

        # 生成可选点，最开始的时候不要开启 star 搜索
        candidates = self.gen(R.AI, starSpread=False)
        # if config.debug2:
        #     print(" =================> Candidates: {}".format(candidates))

        if len(candidates) == 1:
            return candidates[0], 1
        cand_len = len(candidates)
        for i in range(cand_len):
            point = candidates[i]
            # if config.debug:
            #     print('++++++++++++++++++ {} ++++++++++++++++++'.format(point))
            #     print('time: {}'.format(time.clock() - self.startTime))
            # 超时判定并且截断搜索
            if time.clock() - self.startTime > config.timeLimit:
                # if config.debug2:
                #     print('TIME OUT!')
                #     print('Points left: {}'.format(candidates[i:]))
                break
            # if config.debugAB:
            #     print("ROOT ====> {} <==== TOOR".format(point))
            v = self.get_value(R.AI, point, deep, self.MIN, self.MAX)
            # if config.debug2:
            #     print("{} , score {}".format(point, v))
            # 如果比之前的一个好，则把当前位子加入待选位子
            if 0.2 < v < 0.8:
                # time out
                break

            if v == best:
                bestPoints.append(point)
            if v > best:
                best = v
                bestPoints = [point]
        # if config.debug2:
        #     print(bestPoints)
        bestPoints.sort(key=lambda x: fixFour(self.AIScore[x]), reverse=True)
        result = bestPoints[0]
        return result, 0

    def maxmin(self, deep):
        self.MAX = score['FIVE'] * 10
        self.MIN = - score['FIVE'] * 10
        bestPoints = []
        best = self.MIN

        if config.debug:
            print(self.AIScore)

        # 这个函数的作用是生成待选的列表，就是可以下子的空位
        points = self.gen(R.AI, starSpread=True)
        # points = self.genEE(deep)

        if config.debug2:
            print(points)

        # 如果只有一个候选点，直接返回，省时间
        if len(points) == 1:
            return points[0]
        for i in range(len(points)):
            p = points[i]

            if time.clock() - self.startTime > config.timeLimit:
                if config.debug:
                    print('TIME OUT!')
                    print('Points left: {}'.format(points[i:]))
                break
            # 尝试下一个子
            if config.debug3:
                print("ROOT ===> AI takes : {} <=== ROOT".format(p))
            self.put(p, R.AI, True)
            # print("piint {}: {}".format(p, self.AIScore[p]))
            # 找最大值
            v = self.get_min(R.opp, deep - 1, self.MIN, self.MAX)
            # 记得把尝试下的子移除
            self.remove(p)
            if config.debug2:
                print("{} , score {}".format(p, v))
            # 如果比之前的一个好，则把当前位子加入待选位子
            if v == best:
                bestPoints.append(p)
            if v > best:
                best = v
                bestPoints = [p]
        if config.debug2:
            print(bestPoints)
        result_index = np.random.randint(len(bestPoints))
        result = bestPoints[result_index]
        return result

    def get_min(self, player, deep, alpha, beta):
        # 重点来了，评价函数，这个函数返回的是对当前局势的估分

        if deep <= 0:
            r = self.evaluate()
            if config.debug3:
                print('MIN Score ====== {} ======'.format(r))
                print()
            return r

        if config.debug3:
            print('MIN====== {} ======'.format(player))
            # print(self.board)

        v = self.MAX
        points = self.gen(player, starSpread=True)
        if config.debug3:
            print('2 ===> ', points)
        # points = self.genEE(deep)

        for i in range(len(points)):
            p = points[i]
            if config.debug3:
                print("OPP takes : {}".format(p))
            if self.win(player, p):
                return self.MIN
            self.put(p, player, True)
            v = min(v, self.get_max(R.get_opponent(player), deep - 1, alpha, beta))
            # 记得把尝试下的子移除
            self.remove(p)
            # 进行剪枝操作
            if v <= alpha:
                return v
            beta = min(beta, v)

        return v

    def get_max(self, player, deep, alpha, beta):

        if deep <= 0:
            r = self.evaluate()
            if config.debug3:
                print('MAX Score ====== {} ======'.format(r))
                print()
            return r

        if config.debug3:
            print('MAX====== {} ======'.format(player))
            # print(self.board)

        v = self.MIN
        points = self.gen(player, starSpread=True)
        # points = self.genEE(deep)
        if config.debug3:
            print('1 ===> ', points)
        for i in range(len(points)):
            p = points[i]
            if config.debug3:
                print("AI takes : {}".format(p))
            if self.win(player, p):
                return self.MAX
            self.put(p, player, True)
            v = max(v, self.get_min(R.get_opponent(player), deep - 1, alpha, beta))
            # 记得把尝试下的子移除
            self.remove(p)
            # 进行剪枝操作
            if v >= beta:
                return v
            alpha = max(alpha, v)

        return v

    def win(self, player, position=None):
        if position is None:
            if player == R.AI:
                five_ = np.max(self.AIScore)
            elif player == R.opp:
                five_ = np.max(self.oppScore)
            if five_ >= score['FIVE']:
                return player
        else:
            if player == R.AI:
                r = self.AIScore[position[0]][position[1]]
            elif player == R.opp:
                r = self.oppScore[position[0]][position[1]]

            if r >= score['FIVE']:
                return player

        return False


if __name__ == '__main__':
    board = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 2, 0, 2, 1, 2, 2, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 2, 1, 0, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 2, 2, 1, 2, 2, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    BB = Board(board)
    print(BB.AIScore[5, 8])
    # vcf(BB, 1, 10)