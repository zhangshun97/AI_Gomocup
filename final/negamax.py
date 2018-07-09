#
# 思路：
# 每次开始迭代前，先生成一组候选列表，然后在迭代加深的过程中不断更新这个列表中的分数
# 这样迭代的深度越大，则分数越精确，并且，任何时候达到时间限制而中断迭代的时候，能保证这个列表中的分数都是可靠的
#

from role import role
from vcx import vcx
from config import Config
from score import score
from mathMy import *
import time

R = role()
config = Config()

MAX = score['FIVE'] * 10
MIN = -1 * MAX

count = 0  # 每次思考的节点数
PVcut = None
ABcut = None  # AB剪枝次数
cacheCount = 0  # zobrist缓存节点数
cacheGet = 0  # zobrist缓存命中数量

candidates = []
Cache = {}

vcxDeep = None
startTime = None  # 开始时间，用来计算每一步的时间
allBestPoints = None  # 记录迭代过程中得到的全部最好点

#
# max min search
# white is max, black is min
#
value_set = {}


def negamax(b, deep, alpha, beta):
    global count, ABcut, PVcut
    count = 0
    ABcut = 0
    PVcut = 0

    for i in range(len(candidates)):
        p = candidates[i]
        b.put(p, R.AI)
        steps = p
        v = r(b, deep - 1, -beta, -alpha, R.opp, 1, steps[0], 0)
        v['score'] *= -1
        alpha = max(alpha, v['score'])
        b.remove(p)
        value_set[p] = v

        # 超时判定
        # TODO: check
        # if time.clock() - start > config.timeLimit * 1000:
        #     print("timeout......")
        #     break  # time out and quit
    print("迭代完成,deep=", deep)

    return alpha


def r(b, deep, alpha, beta, player, step, steps, spread):
    global cacheGet, count, ABcut
    if config.cache:
        c = Cache.get(b.zobrist.boardHashing, None)
        if c:
            if c['deep'] >= deep:
                # 如果缓存中的结果搜索深度不比当前小，则结果完全可用
                cacheGet += 1
                # 记得clone，因为这个分数会在搜索过程中被修改，会使缓存中的值不正确
                return {
                    'score': c['score']['score'],
                    'steps': steps,
                    'c': c,
                }
            else:
                # 如果缓存的结果中搜索深度比当前小，那么任何一方出现双三及以上结果的情况下可用
                # TODO: 只有这一个缓存策略是会导致开启缓存后会和以前的结果有一点点区别的，其他几种都是透明的缓存策略
                if greatOrEqualThan(c['score'], score['FOUR']) or littleOrEqualThan(c['score'], -score['FOUR']):
                    cacheGet += 1
                    return c['score']

    _e = b.evaluate(role)

    leaf = {
        'score': _e,
        'step': step,
        'steps': steps,
    }

    count += 1
    # 搜索到底 或者已经胜利
    # 注意这里是小于0，而不是1，因为本次直接返回结果并没有下一步棋
    if deep <= 0 or greatOrEqualThan(_e, score['FIVE']) or littleOrEqualThan(_e, score['FIVE']):
        # 经过测试，把算杀放在对子节点的搜索之后，比放在前面速度更快一些
        return leaf

    best = {
        'score': MIN,
        'step': step,
        'steps': steps,
    }

    # 双方个下两个子之后，开启 star spread 模式
    points = b.gen(player, step > 2, step > 4)

    if not points:
        return leaf

    for i in range(len(points)):
        p = points[i]
        b.put(p, player)

        _deep = deep - 1
        _spread = spread

        if _spread < config.spreadLimit:
            # 冲四延伸
            if (player == R.AI and b.scoreOop[p] >= score['FIVE']) or (
                    player == R.opp and b.scoreAI[p] >= score['FIVE']):
                _deep += 2
                _spread += 1

        _steps = steps[0]
        _steps.append(p)
        v = r(b, _deep, -beta, -alpha, R.get_opponent(player), step + 1, _steps, _spread)
        v['score'] *= -1
        b.remove(p)

        # 注意，这里决定了剪枝时使用的值必须比MAX小
        if v['score'] > best['score']:
            best = v

        alpha = max(best['score'], alpha)
    # AB 剪枝
    # 这里不要直接返回原来的值，因为这样上一层会以为就是这个分，实际上这个节点直接剪掉就好了，根本不用考虑，也就是直接给一个很大的值让他被减掉
    # 这样会导致一些差不多的节点都被剪掉，但是没关系，不影响棋力
    # 一定要注意，这里必须是 greatThan 即 明显大于，而不是 greatOrEqualThan 不然会出现很多差不多的有用分支被剪掉，会出现致命错误
    if greatOrEqualThan(v['score'], beta):
        ABcut += 1
        v['score'] = MAX - 1  # 被剪枝的，直接用一个极大值来记录，但是注意必须比MAX小
        v['abcut'] = 1  # 剪枝标记
        return v


    cache(b, deep, best)

    return best


def cache(b, deep, score_):
    global cacheCount, Cache
    if not config.cache:
        return False
    if score_['abcut']:
        # 被剪枝的不要缓存哦，因为分数是一个极值
        return False
    obj = {
        'deep': deep,
        'score': {
            'score': score_['score'],
            'steps': score_['steps'],
            'step': score_['step'],
        },
    }
    Cache[b.zobrist.boardHashing] = obj
    cacheCount += 1


def deeping(b, deep):
    candidates = b.gen(R.AI)
    start = time.clock()
    deep = config.searchDeep if deep is None else deep
    # 每次开始迭代的时候清空缓存。这里缓存的主要目的是在每一次的时候加快搜索，
    # 而不是长期存储。事实证明这样的清空方式对搜索速度的影响非常小（小于10%)
    global Cache
    Cache = {}

    for i in range(2, deep + 1, 2):
        bestScore = negamax(b, i, MIN, MAX)
        # 每次迭代剔除必败点，直到没有必败点或者只剩最后一个点
        # 实际上，由于必败点几乎都会被AB剪枝剪掉，因此这段代码几乎不会生效
        if greatOrEqualThan(bestScore, score['FIVE']):
            # 能赢了
            # 下面这样做，会导致上一层的分数，在这一层导致自己被剪枝的bug，因为我们的判断条件是 >=，
            # 上次层搜到的分数，在更深一层搜索的时候，会因为满足 >= 的条件而把自己剪枝掉
            break

    # TODO: 美化一下?? 不知道有没有影响

    # 排序
    # 经过测试，这个如果放在上面的for循环中（就是每次迭代都排序），反而由于迭代深度太浅，排序不好反而会降低搜索速度
    # TODO: check if skey is right
    # def skey(x):
    print("candidates without sorting: ", candidates)
    # candidates.sort(key=skey, reverse=True)

    best = candidates[0]
    bestPoints = []
    for cand in candidates:
        if greatOrEqualThan(cand['score'], best['score']) and cand['step'] == best['step']:
            bestPoints.append(cand)
    result = candidates[0]
    if config.log:
        print("可选节点：", bestPoints)
        print("选择节点：", candidates[0], ", 分数:", result['score'], ", 步数:", result['step'])
        print('搜索节点数:', count, ',AB剪枝次数:', ABcut, ', PV剪枝次数:', PVcut)
        print('搜索缓存:', '总数', cacheCount, ', 命中率 ', (cacheGet / cacheCount * 100), '%, ', cacheGet, '/', cacheCount)
        print('当前统计：', count, '个节点, 耗时:', time.clock() - start, 's, NPS:')
        print("===============统计表===============")

    return result
