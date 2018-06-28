class Config:

    def __init__(self):
        # config
        self.opening = True   # 使用开局库
        self.searchDeep = 4   # 搜索深度
        self.countLimit = 10  # gen函数返回的节点数量上限，超过之后将会按照分数进行截断
        self.timeLimit = 10   # 时间限制，秒
        self.vcxDeep = 5      # 算杀深度
        self.random = False   # 在分数差不多的时候是不是随机选择一个走
        self.log = False
        # 下面几个设置都是用来提升搜索速度的
        self.spreadLimit = 1  # 单步延伸 长度限制
        self.star = False     # 是否开启 starspread
        # TODO = 目前开启缓存后，搜索会出现一些未知的bug
        self.cache = True     # 使用缓存, 其实只有搜索的缓存有用，其他缓存几乎无用。因为只有搜索的缓存命中后就能剪掉一整个分支，
                              # 这个分支一般会包含很多个点。而在其他地方加缓存，每次命中只能剪掉一个点，影响不大。
        self.window = False   # 启用期望窗口，由于用的模糊比较，所以和期望窗口是有冲突的

        # 调试
        self.debug = False     # 打印详细的debug信息
        self.debug2 = True     # 打印每一个候选点的得分
        self.debug3 = False    # 打印 MINI-MAX 搜索的具体步骤
        self.debugGen = False  # 调试启发式搜索函数s
