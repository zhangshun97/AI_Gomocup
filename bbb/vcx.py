"============="
"=== V C X ==="
"============="
#
# 算杀
# 算杀的原理和极大极小值搜索是一样的
# 不过算杀只考虑冲四活三这类对方必须防守的棋
# 因此算杀的复杂度虽然是 M^N ，但是底数M特别小，可以算到16步以上的杀棋。
# VCT 连续活三胜
# VCF 连续冲四胜利
#

#
# 基本思路
# 电脑有活三或者冲四，认为是玩家必须防守的
# 玩家防守的时候却不一定根据电脑的棋来走，而是选择走自己最好的棋，比如有可能是自己选择冲四
#

import numpy as np
from role import role
from config import Config
from score import score

R = role()
config = Config()

Cache = {
    'vct': {},
    'vcf': {},
}

# debugNodeCount = 0

# MAX_SCORE = score['THREE']
# MIN_SCORE = score['FOUR']
MAX_SCORE = score['FOUR']
MIN_SCORE = score['THREE']

lastMaxPoint = None
lastMinPoint = None


# 找到所有比目标分数大的位置
# 注意，不止要找自己的，还要找对面的，
def findMax(self, player, score_):
    # assert player==1 #max jiedian de wan jia wei 1
    result = []
    fives = []

    for i in range(self.height):
        for j in range(self.width):
            if self.board[i][j] != R.empty:
                continue
            p = (i, j)

            # 注意，防一手对面冲四
            # 所以不管谁能连成五，先防一下
            if self.oppScore[p[0]][p[1]] >= score['FIVE']:
                # assert 0
                self.score[p] = self.oppScore[p[0]][p[1]]
                if player == R.AI:
                    self.score[p] *= -1
                fives.append(p)
            elif self.AIScore[p[0]][p[1]] >= score['FIVE']:
                # assert 0
                self.score[p] = self.AIScore[p[0]][p[1]]
                if player == R.opp:
                    self.score[p] *= -1
                fives.append(p)
            else:
                if (not lastMaxPoint) or (i == lastMaxPoint[0] or j == lastMaxPoint[1] or \
                                        (np.abs(i - lastMaxPoint[0]) == np.abs(j - lastMaxPoint[1]))):
                    # 如果没有lastmaxpoint，或者
                    # print("if (not lastMaxPoint) or (i == lastMaxPoint[0] or j == lastMaxPoint[1] or \
                    #                     (np.abs(i - lastMaxPoint[0]) == np.abs(j - lastMaxPoint[1]))):")
                    s = self.AIScore[p[0]][p[1]] if player == R.AI else self.oppScore[p[0]][p[1]]
                    self.score[p] = s
                    if s >= score_:
                        #这句话是什么意思？
                        # print(p,"p")
                        # print(s)
                        result.append(p)
    # 能连五，则直接返回
    # 但是注意不要碰到连五就返回，而是把所有连五的点都考虑一遍，不然可能出现自己能连却防守别人的问题
    if fives:
        # print(fives,"five")
        return fives
    # 注意对结果进行排序
    result.sort(key=lambda x: self.score[x], reverse=True)
    # if len(result):
        # print( player, score_,result)
    return result


# MIN层
# 找到所有比目标分数大的位置
# 这是MIN层，所以己方分数要变成负数
def findMin(self, player, score_):
    result = []
    fives = []
    fours = []
    blockedfours = []
    for i in range(self.height):
        for j in range(self.width):
            if self.board[i][j] == R.empty:
                p = (i, j)
                # print(player)

                s1 = self.oppScore[p] #if player == R.AI else self.oppScore[p]
                s2 = self.AIScore[p] #if player == R.AI else self.AIScore[p]
                if s1 >= score['FIVE']:#如果对面有5，直接返回！
                    self.score[p] = -s1
                    return [p]
                if s2 >= score['FIVE']:#如果我有5，直接返回！
                    self.score[p] = s2
                    fives.append(p)
                    continue
                if s1 >= score['FOUR']:#如果对面有开4
                    self.score[p] = -s1
                    fours.insert(0, p)
                    continue
                if s2 >= score['FOUR']:#如果我有开四
                    self.score[p] = s2
                    fours.append(p)
                    continue
                if s1 >= score['BLOCKED_FOUR']:#如果对面有冲4
                    self.score[p] = -s1
                    blockedfours.insert(0, p)
                    continue
                if s2 >= score['BLOCKED_FOUR']:
                    self.score[p] = s2
                    blockedfours.append(p)
                    continue
                if s1 >= score_ or s2 >= score_:
                    p = (i, j)
                    self.score[p] = s1
                    result.append(p)

    # if fives:
    #     return fives

    # 注意冲四，因为虽然冲四的分比活四低，但是他的防守优先级是和活四一样高的，否则会忽略冲四导致获胜的走法
    if len(fours)!=0:
        return fours + blockedfours+fives

    # 注意对结果进行排序
    # 因为 fours 可能不存在，这时候不要忽略了 blockedfours
    result = blockedfours + result+fives #这里让我返回可能的点
    result.sort(key=lambda x: np.abs(self.score[x]), reverse=True)
    return result


def get_max(self, player, deep, totalDeep=0):
    # debugNodeCount += 1
    global lastMaxPoint
    if deep <= 1:
        return False
    points = findMax(self, player, MAX_SCORE)
    #先找有没有4的情况
    if points and self.score[points[0]] >= score['FOUR']:
        # print("This is four")
        # print(score["FOUR"])
        # 为了减少一层搜索，活四就行了
        return [points[0]]
    if len(points) == 0:
        return False

    for i in range(len(points)):
        p = points[i]
        self.put(p, player, True)
        # 如果是防守对面的冲四，那么不用记下来
        if not self.score[p] <= -score['FIVE']:
            #记录下一次的最好值
            lastMaxPoint = p

        m = get_min(self, R.get_opponent(player), deep - 1)
        self.remove(p)
        if m:
            # print(m)
            # 这里返回下一层的值
            m.insert(0, p)
            # print(m,"this is m")
            return m
        # else:
        #     print("there we return [p]",p)
        #     return [p]

    return False


# 只要有一种方式能防守住，就可以了
def get_min(self, player, deep):
    # debugNodeCount += 1
    global lastMinPoint
    w = self.win(player)

    if w == player:
        return False
    # if self.win(R.get_opponent(player)):
    #     return True
    if deep <= 1:
        return False
    points = findMin(self, player, MIN_SCORE)
    if points and -1 * self.score[points[0]] >= score['FOUR']:
        # 如果对面走了最好的点！赢了！
        return False
    if len(points) == 0:
        #这里为什么？
        return False

    cands = []
    for i in range(len(points)):
        p = points[i]
        """ zheli de player shi hou mian gai de !"""
        self.put(p, player,True)
        lastMinPoint = p
        m = get_max(self, R.get_opponent(player), deep - 1)#这个里面对每一种找到必杀！
        self.remove(p)
        if m:
            # print(m)
            m.insert(0, p)
            cands.append(m)
            continue
        else:
            # 只要有一种能防守住，因为是对面选择，这个路径的必杀失败！
            return False
    _i = np.random.randint(len(cands))
    #赢了！随便返回一个？
    result = cands[_i]
    return result


def deeping(self, player, deep, totalDeep):
    # 迭代加深算法！
    global lastMinPoint, lastMaxPoint  # ,debugNodeCount
    # debugNodeCount = 0
    for i in range(1, deep + 1):
        lastMinPoint = None
        lastMaxPoint = None
        result = get_max(self, player, i, deep)
        if result:
            # print("There we just get the solution")
            # print(result)
            # print(i)
            # 找到一个就行
            break
    return result


def vcx(self, player, onlyFour, deep=None):
    deep = config.vcxDeep if deep is None else deep
    global MAX_SCORE, MIN_SCORE
    if deep <= 0:
        return False
    if onlyFour:
        # 计算通过 冲四 赢的
        # MAX_SCORE = score['THREE']
        # MIN_SCORE = score['THREE']
        MAX_SCORE = score['BLOCKED_FOUR']
        MIN_SCORE = score['FIVE']
        result = deeping(self, player, deep, deep)
        # print(result)
        if result:
            # assert len(result) == 1
            # self.score[result[0]] = score['FOUR']
            return result[0]
        return False
    else:
        # 计算通过 活三 赢的
        # MAX_SCORE = score['THREE']
        # MIN_SCORE = score['THREE']
        MAX_SCORE = score['THREE']
        MIN_SCORE = score['BLOCKED_FOUR']
        result = deeping(self, player, deep, deep)
        if result:
            # assert len(result) == 1
            # self.score[result[0]] = score['THREE'] * 2
            return result[0]
        return result


def cache(self, result, vcf=False):
    if not config.cache:
        return
    if vcf:
        Cache['vcf'][self.zobrist.boardHashing[0]] = result
    else:
        Cache['vct'][self.zobrist.boardHashing[0]] = result


def getCache(self, vcf=False):
    if not config.cache:
        return
    if vcf:
        result = Cache['vcf'].get(self.zobrist.boardHashing[0], None)
    else:
        result = Cache['vct'].get(self.zobrist.boardHashing[0], None)
    return result


# 连续冲四
def vcf(self, player, deep):
    c = getCache(self, True)
    if c:
        return c
    else:
        result = vcx(self, player, True, deep)
        cache(self, result, True)
        return result


# 连续活三
def vct(self, player, deep):
    c = getCache(self)
    if c:
        return c
    else:
        result = vcx(self, player, False,deep)
        cache(self, result, False)
        return result
