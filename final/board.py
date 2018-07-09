import numpy as np
from role import role
from zobrist import Zobrist
from evaluate import evaluate_position as scorePoint
from config import Config
from score import score
import time

count = 0
total = 0

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


class Board:

    def __init__(self, board):
        self.board = np.array(board).copy()
        self.height = len(board)
        self.width = len(board[0])
        assert self.width == self.height, "board is not square"
        self.size = self.width

        self.scoreCache = np.zeros([2, 4, self.height, self.width])
        self.evaluateCache = {}

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

        # scoreCache[role][dir][row][column]
        self.scoreCache = np.zeros([3, 4, self.height, self.width])
        self.initScore()
        # TODO: check the usage of this table
        # self.statisticTable = np.zeros([self.height, self.width])

    def initScore(self):
        # TODO: check if this is equivalent to the p.item thing
        self.attack = {}
        self.score = {}
        self.role = {}
        self.scoreHum = {}
        self.scoreCom = {}
        emptys = []

        # 注意初始化分数的更新顺序！
        for i in range(self.height):
            for j in range(self.width):
                # get score for both players
                if self.board[i, j] == R.empty:
                    if self.hasNeighbor((i, j), 1, 1) or self.hasNeighbor((i, j), 2, 2):
                        emptys.append((i, j))
                else:
                    self.updateScore((i, j))
                    self.steps.append((i, j))
        for p in emptys:
            self.AIScore[p] = scorePoint(self, p, R.AI)
            self.oppScore[p] = scorePoint(self, p, R.opp)

    # 只更新一个点附近的分数
    # 参见 evaluate 中的代码，为了优化性能，在更新分数的时候可以指定只更新某一个方向的分数
    def updateScore(self, position):
        def update(position, direction):
            role_ = self.board[position]
            if role_ != R.get_opponent(R.AI):
                AIS = scorePoint(self, position, R.AI, direction)
                self.AIScore[position] = AIS
                # print(AIS, '----')
                # self.statisticTable[position] += AIS
            else:
                self.AIScore[position] = 0

            if role_ != R.get_opponent(R.opp):
                oppS = scorePoint(self, position, R.opp, direction)
                self.oppScore[position] = oppS
                # self.statisticTable[position] += oppS
            else:
                self.oppScore[position] = 0

        radius = 6
        # update no matter empty or not
        # --
        for i in range(-radius, radius):
            x, y = position[0], position[1] + i
            if y < 0:
                continue
            elif y >= self.size:
                break
            else:
                update((x, y), 0)
        # |
        for i in range(-radius, radius):
            x, y = position[0] + i, position[1]
            if x < 0:
                continue
            elif x >= self.size:
                break
            else:
                update((x, y), 1)
        # \
        for i in range(-radius, radius):
            x, y = position[0] + i, position[1] + i
            if x < 0 or y < 0:
                continue
            elif x >= self.size or y >= self.size:
                break
            else:
                update((x, y), 2)
        # /
        for i in range(-radius, radius):
            x, y = position[0] + i, position[1] - i
            if x < 0 or y >= self.size:
                continue
            elif x >= self.size or y < 0:
                break
            else:
                update((x, y), 3)

    # get next move
    def put(self, position, player, record):
        if config.debug:
            print(player, 'put [', position, ']')
        self.board[position] = player
        self.zobrist.go(position, player)
        if record:
            self.steps.append(position)
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

    # TODO: remove a step
    def remove(self, position):
        r = self.board[position]
        if config.debug:
            print(r, 'remove [', position, ']')
        self.zobrist.go(position, r)
        self.board[position] = R.empty
        self.updateScore(position)
        self.allSteps.pop()

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
    def evaluate(self, player=None):
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
        result = self.AIMaxScore - self.oppMaxScore

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

    def gen(self, player, onlyThrees=False, starSpread=False):
        if config.debugGen:
            print("====== GEN for {} ======".format(player))
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
        global count, total
        lastPoint1 = None
        lastPoint2 = None

        # 默认情况下 我们遍历整个棋盘。但是在开启star模式下，我们遍历的范围就会小很多
        # 只需要遍历以两个点为中心正方形。
        # 注意除非专门处理重叠区域，否则不要把两个正方形分开算，因为一般情况下这两个正方形会有相当大的重叠面积，别重复计算了
        startI = 0
        startJ = 0
        endI = self.size - 1
        endJ = self.size - 1
        if len(self.allSteps) >= 2 and starSpread and config.star:

            i = len(self.allSteps) - 1
            while not lastPoint1 and i >= 0:
                p = self.allSteps[i]
                if self.role.get(p, None) != player and self.attack.get(p, None) != player:
                    lastPoint1 = p
                i -= 2

            if not lastPoint1:
                if self.role.get(self.allSteps[0], None) != player:
                    lastPoint1 = self.allSteps[0]
                else:
                    lastPoint1 = self.allSteps[1]
            i = len(self.allSteps) - 2
            while not lastPoint2 and i >= 0:
                p = self.allSteps[i]
                if self.attack.get(p, None):
                    lastPoint2 = p
                i -= 2

            if not lastPoint2:
                if self.role.get(self.allSteps[0], None) == player:
                    lastPoint2 = self.allSteps[0]
                else:
                    lastPoint2 = self.allSteps[1]

            # 根据双方最后的进攻点周围展开搜索
            if config.debug:
                print("1 attack point: {}, 2 attack point: {}".format(lastPoint1, lastPoint2))

            startI = min(lastPoint1[0] - 5, lastPoint2[0] - 5)
            startJ = min(lastPoint1[1] - 5, lastPoint2[1] - 5)
            startI = max(0, startI)
            startJ = max(0, startJ)
            endI = max(lastPoint1[0] + 5, lastPoint2[0] + 5)
            endJ = max(lastPoint1[1] + 5, lastPoint2[1] + 5)
            endI = min(self.size - 1, endI)
            endJ = min(self.size - 1, endJ)

        for i in range(startI, endI + 1):
            for j in range(startJ, endJ + 1):
                p = (i, j)
                if self.board[i][j] == R.empty:
                    neighbor = (2, 2)
                    if len(self.steps) < 6:
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

                        total += 1
                        # 双星延伸，以提升性能
                        # 思路：每次下的子，只可能是自己进攻，或者防守对面（也就是对面进攻点）
                        # 我们假定任何时候，绝大多数情况下进攻的路线都可以按次序连城一条折线，那么每次每一个子，一定都是在上一个己方棋子的八个方向之一。
                        # 因为既可能自己进攻，也可能防守对面，所以是最后两个子的米子方向上
                        # 那么极少数情况，进攻路线无法连成一条折线呢?很简单，我们对前双方两步不作star限制就好，这样可以 兼容一条折线中间伸出一段的情况
                        if lastPoint1 and lastPoint2 and config.star:
                            # 距离必须在5步以内
                            if (np.abs(i - lastPoint1[0]) > 5 or np.abs(j - lastPoint1[1]) > 5) and \
                                    (np.abs(i - lastPoint2[0]) > 5 or np.abs(j - lastPoint2[1]) > 5):
                                count += 1
                                continue
                            # 必须在米子方向上
                            if maxScore >= score['FIVE'] or \
                                    (i == lastPoint1[0] or j == lastPoint1[1] or (
                                            np.abs(i - lastPoint1[0]) == np.abs(j - lastPoint1[1]))) \
                                    or (i == lastPoint2[0] or j == lastPoint2[1] or (
                                    np.abs(i - lastPoint2[0]) == np.abs(j - lastPoint2[1]))):
                                pass
                            else:
                                count += 1
                                continue

                        if scoreAI >= score['FIVE']:
                            # 先看电脑能不能连成 5
                            return [p]
                        elif scoreOpp >= score['FIVE']:
                            # 再看玩家能不能连成 5
                            # 别急着返回，因为遍历还没完成，说不定电脑自己能成五
                            fives.append(p)
                        elif scoreAI >= score['FOUR']:
                            AIfours.append(p)
                        elif scoreOpp >= score['FOUR']:
                            oppfours.append(p)
                        elif scoreAI >= score['BLOCKED_FOUR']:
                            AIblockedfours.append(p)
                        elif scoreOpp >= score['BLOCKED_FOUR']:
                            oppblockedfours.append(p)
                        elif scoreAI >= 2 * score['THREE']:  # 能成双三也很强
                            AItwothrees.append(p)
                        elif scoreOpp >= 2 * score['THREE']:
                            opptwothrees.append(p)
                        elif scoreAI >= score['THREE']:
                            AIthrees.append(p)
                        elif scoreOpp >= score['THREE']:
                            oppthrees.append(p)
                        elif scoreAI >= score['TWO']:
                            AItwos.append(p)
                        elif scoreOpp >= score['TWO']:
                            opptwos.append(p)
                        else:
                            neighbors.append(p)
        if config.debugGen:
            print(
                'fives', fives, '\n',
                'AIfours', AIfours, '\n',
                'AI23', AItwothrees, '\n',
                'AI4s', AIblockedfours, '\n',
                'AI3s', AIthrees, '\n',
            )
            print(
                'oppfours', oppfours, '\n',
                'opp23s', opptwothrees, '\n',
                'opp4s', oppblockedfours, '\n',
                'opp3s', oppthrees, '\n',
            )
        # 如果成五，是必杀棋，直接返回
        if fives:
            return fives
        # 自己能活四，则直接活四，不考虑冲四
        if player == R.AI and AIfours:
            return AIfours
        if player == R.opp and oppfours:
            return oppfours

        # 对面有活四冲四，自己冲四都没，则只考虑对面活四 （此时对面冲四就不用考虑了)
        if player == R.AI and oppfours and not AIblockedfours:
            return oppfours
        if player == R.opp and AIfours and not oppblockedfours:
            return AIfours

        # 对面有活四自己有冲四，则都考虑下
        fours = AIfours + oppfours if player == R.AI else oppfours + AIfours
        blockedfours = AIblockedfours + oppblockedfours if player == R.opp else oppblockedfours + AIblockedfours
        if fours:
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

        # 双三很特殊，因为能形成双三的不一定比一个活三强
        if AItwothrees or opptwothrees:
            return result

        # 只返回大于等于活三的棋
        if onlyThrees:
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
            return result[:config.countLimit]

        return result

    # def genE(self, depth):
    #     neighbors = []
    #     nextNeighbors = []
    #
    #     for i in range(self.height):
    #         for j in range(self.width):
    #             if self.board[i][j] == R.empty:
    #                 if self.hasNeighbor((i, j), 1, 1):
    #                     neighbors.append((i, j))
    #                 elif depth >= 2 and self.hasNeighbor((i, j), 2, 2):
    #                     nextNeighbors.append((i, j))
    #     return neighbors + nextNeighbors
    #
    # def genEE(self, deep):
    #     fives = []
    #     fours = []
    #     twothrees = []
    #     threes = []
    #     twos = []
    #     neighbors = []
    #     nextNeighbors = []
    #
    #     for i in range(self.height):
    #         for j in range(self.width):
    #             if self.board[i][j] != R.empty:
    #                 continue
    #             p = (i, j)
    #             if self.hasNeighbor((i, j), 1, 1):
    #                 scoreOpp = self.oppScore[i][j]
    #                 scoreAI = self.AIScore[i][j]
    #
    #                 if scoreAI >= score['FIVE']:
    #                     # 先看电脑能不能连成 5
    #                     fives.append(p)
    #                 elif scoreOpp >= score['FIVE']:
    #                     # 再看玩家能不能连成 5
    #                     # 别急着返回，因为遍历还没完成，说不定电脑自己能成五
    #                     fives.append(p)
    #                 elif scoreAI >= score['FOUR']:
    #                     fours.insert(0, p)
    #
    #                 elif scoreOpp >= score['FOUR']:
    #                     fours.append(p)
    #                 elif scoreAI >= 2 * score['THREE']:  # 能成双三也很强
    #                     twothrees.insert(0, p)
    #                 elif scoreOpp >= 2 * score['THREE']:
    #                     twothrees.append(p)
    #                 elif scoreAI >= score['THREE']:
    #                     threes.insert(0, p)
    #                 elif scoreOpp >= score['THREE']:
    #                     threes.append(p)
    #                 elif scoreAI >= score['TWO']:
    #                     twos.insert(0, p)
    #                 elif scoreOpp >= score['TWO']:
    #                     twos.insert(0, p)
    #                 else:
    #                     neighbors.append(p)
    #             elif deep >= 2 and self.hasNeighbor((i, j), 2, 2):
    #                 pass
    #                 # nextNeighbors.append(p)
    #     if fives:
    #         return [fives[0]]
    #     elif fours:
    #         return fours
    #     elif twothrees:
    #         return twothrees
    #     else:
    #         return threes + twos + neighbors + nextNeighbors

    def hasNeighbor(self, position, distance, count):
        # this function will check the exact surrounding of the position
        # return TRUE is there are >= count neighbors
        # for example: distance = 1
        #  XXX
        #  XOX
        #  XXX
        # all the 'X's are neighbors of 'O'
        # 缓存加速
        if self.neighborCache.get(position, 0) >= distance:
            return True
        startX = position[0] - distance
        endX = position[0] + distance
        startY = position[1] - distance
        endY = position[1] + distance
        for i in range(startX, endX + 1):
            if i < 0 or i >= self.size:
                continue
            for j in range(startY, endY + 1):
                if j < 0 or j >= self.size:
                    continue
                if i == position[0] and j == position[1]:
                    continue
                if self.board[i][j] != R.empty:
                    count -= 1
                    if count <= 0:
                        # TODO: 如果考虑 '悔棋' 的话这样做是不对的
                        self.neighborCache[position] = distance
                        return True
        return False

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
            if config.debug:
                print('++++++++++++++++++ {} ++++++++++++++++++'.format(p))
                print('time: {}'.format(time.clock() - self.startTime))
            if time.clock() - self.startTime > config.timeLimit:
                if config.debug:
                    print('TIME OUT!')
                    print('Points left: {}'.format(points[i:]))
                break
            # 尝试下一个子
            self.put(p, R.AI, True)
            # print("piint {}: {}".format(p, self.AIScore[p]))
            # 找最大值
            v = self.get_min(R.opp, deep - 1, self.MIN, self.MAX)
            # 记得把尝试下的子移除
            self.remove(p)
            # 如果跟之前的一个好，则把当前位子加入待选位子
            if config.debug2:
                print("{} , score {}".format(p, v))
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
        if config.debug:
            print('MIN====== {} ======'.format(player))
            # print(self.board)

        if deep <= 0:
            r = self.evaluate(player)
            if config.debug:
                print('MIN====== {} ======'.format(r))
            return r

        v = self.MAX
        points = self.gen(player, starSpread=True)
        if config.debug3:
            print('2 ===> ', points)
        # points = self.genEE(deep)

        for i in range(len(points)):
            p = points[i]
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
        if config.debug:
            print('MAX====== {} ======'.format(player))
            print(self.board)

        if deep <= 0:
            r = self.evaluate(player)
            if config.debug:
                print('MAX====== {} ======'.format(r))
            return r

        v = self.MIN
        points = self.gen(player, starSpread=True)
        # points = self.genEE(deep)
        if config.debug3:
            print('1 ===> ', points)
        for i in range(len(points)):
            p = points[i]
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
            for i in range(self.height):
                for j in range(self.width):
                    t = self.board[i][j]
                    if t == R.empty:
                        r = self.isFive((i, j), player)
                        if r:
                            return player
        else:
            r = self.isFive(position, player)
            if r:
                return player

        return False

    # 判断 player 下了这个点之后有没有成 5
    def isFive(self, p, player):
        size = self.size
        count = 1

        def reset():
            nonlocal count
            count = 1

        # --
        for i in range(p[1] + 1, size + 1):
            if i >= size:
                break
            t = self.board[p[0]][i]
            if t != player:
                break
            count += 1

        for i in range(p[1] - 1, -1, -1):
            if i < 0:
                break
            t = self.board[p[0]][i]
            if t != player:
                break
            count += 1

        if count >= 5:
            return True

        # |
        reset()
        for i in range(p[0] + 1, size + 1):
            if i >= size:
                break
            t = self.board[i][p[1]]
            if t != player:
                break
            count += 1

        for i in range(p[0] - 1, -1, -1):
            if i < 0:
                break
            t = self.board[i][p[1]]
            if t != player:
                break
            count += 1

        if count >= 5:
            return True

        # \
        reset()
        for i in range(1, size + 1):
            x, y = p[0] + i, p[1] + i
            if x >= size or y >= size:
                break
            t = self.board[x][y]
            if t != player:
                break
            count += 1

        for i in range(1, size + 1):
            x, y = p[0] - i, p[1] - i
            if x < 0 or y < 0:
                break
            t = self.board[x][y]
            if t != player:
                break
            count += 1

        if count >= 5:
            return True

        # /
        reset()

        for i in range(1, size + 1):
            x, y = p[0] + i, p[1] - i
            if x >= size or y < 0:
                break
            t = self.board[x][y]
            if t != player:
                break
            count += 1

        for i in range(1, size + 1):
            x, y = p[0] - i, p[1] + i
            if x < 0 or y >= size:
                break
            t = self.board[x][y]
            if t != player:
                break
            count += 1

        if count >= 5:
            return True

        return False


if __name__ == '__main__':
    board = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
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

    BB = Board(board)

    print(BB.AIScore)
