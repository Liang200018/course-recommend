import random
from abc import ABC, abstractmethod
from course.recommend import ItemCF, LFMRecommend
from course.icf import ICF

class Recommend:
    '''所有推荐模型的基类'''
    def __init__(self, model):
        self.model = model
    
    # def recommend(self, user, N):
    #     """
    #     model的推荐方法的统一封装
    #     :return list  
    #     """
    #     ru = []
    #     return ru

    def precision(self, train, test, N):
        # N是给用户推荐N个物品
        hit = 0 # 记录所有用户的推荐命中数
        all = 0
        for user, items in train.items():
            
            ru = self.recommend(user, N=N) # Recommend是所有推荐方法的接口
            if test.get(user) is None: # 测试集中没有用户的数据
                continue
            tu = test[user]
            hit += len(set(ru) & set(tu))
            all += N 
        return hit / (all * 1.0)
    
    def recall(self, train, test, N):
        hit = 0 
        all = 0
        for user, items in train.items():
            ru = self.recommend(user, N=N) # Recommend是所有推荐方法的接口
            if test.get(user) is None: # 测试集中没有用户的数据
                continue
            tu = test[user]
            hit += len(set(ru) & set(tu))
            all += len(tu) 
        return hit / (all * 1.0)    
    
    def coverage(self, train, test, N):
        # 被推荐的物品占总物品的比例, 总物品可以理解为所有的总物品
        # 极端的一个例子，所有人都被推荐了同样的10个物品，那么覆盖率就很低
        items_set = set()
        recommend_items_set = set()
        for user, item in train.items():
            ru = self.recommend(user, N=N)
            for i in train[user]:
                items_set.add(i)
            for i in ru:
                recommend_items_set.add(i)
        return  len(recommend_items_set) / (len(items_set) * 1.0)



class ItemCFModel(Recommend):
    
     
    
    def __init__(self, model, **kwargs):
        self.model = model
        limit_num = kwargs['limit_num'] if kwargs['limit_num'] else None 
        self.model.get_data_from_db(limit_num=limit_num)
        # 模型训练数据， 默认全部，测试时可以给传比较小的数字
        
        self.parameters = {} # 模型的参数
        # 得到全部的数据集
        self.user_items = self.model.get_user_items()
        
    
    def fit(self, train):
        '''传入训练集数据， 训练模型'''
        self.parameters['W'] = self.model.ItemSimilarity(train=train)
        self.parameters['train'] = train
    
    def recommend(self, user, N):
        """
        给每个用户推荐，产生TOPN推荐列表; 模型计算准确度、召回率，需要该方法。
        Parameters
        ----------
        user : TYPE
            DESCRIPTION.
         : TYPE
            DESCRIPTION.

        Returns
        -------
        ru : TYPE
            DESCRIPTION.

        """
        train = self.parameters['train'] 
        W = self.parameters['W']
        
        res = self.model.recommend_to_one(train=train, user=user, W=W)[0:N]       
        ru = [tum[0] for tum in res] 
        return ru

class LFModel(Recommend):
    
    def __init__(self, model, **kwargs):
        self.model = model
        limit_num = kwargs['limit_num'] if kwargs['limit_num'] else None 
        self.model.get_data_from_db(limit_num=limit_num)
        
        self.parameters = {} # 模型的参数
        # 得到全部的数据集
        self.user_items = self.model.get_user_items()
        
    def fit(self, train, **kwargs):
        '''传入训练集数据，训练模型
        train :dict {user: []}
        args: F, N, alpha, lambda_, ntimes
        '''
        self.model.lazy_init(**kwargs)
        self.model.InitModel() # P用户-兴趣矩阵， Q兴趣-物品矩阵
        self.model.LatentFactorModel(user_items=self.user_items, train=train)
        
        
        self.parameters['P'] = self.model.P
        self.parameters['Q'] = self.model.Q
        self.parameters['F'] = self.model.F
        self.parameters['N'] = self.model.N
        self.parameters['alpha'] = self.model.alpha
        self.parameters['lambda_'] = self.model.lambda_
        self.parameters['ntimes'] = self.model.ntimes
        self.parameters['hot_rank'] = self.model.hot_rank
        
    def recommend(self, user, N):
        """
        Parameters
        ----------
        user : TYPE
            DESCRIPTION.
        N : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        res = self.model.recommend_to_one(user, N)
        ru = [tum[0] for tum in res] 
        return ru


class ICFModel(Recommend):
    
    def __init__(self, model, **kwargs):
        self.model = model
        self.parameters = {} # 模型的参数
        
    def fit(self, train, items_pool, user_pool):
        
        self.model.prepareCompute(items_pool, user_pool, train)
        self.model.preCompute(train)
        
        self.parameters['Items'] = self.model.Items
        self.parameters['Users'] = self.model.Users
        self.parameters['Int'] = self.model.Int
        self.parameters['S'] = self.model.S
        self.parameters['N'] = self.model.N
        self.parameters['train'] = train
        
    def recommend(self, user, N):
        """给每个用户推荐，产生TOPN推荐列表; 模型计算准确度、召回率，需要该方法。
        
        Parameters
        ----------
        user : Str
        N : Int

        Returns
        -------
        ru : TYPE
            DESCRIPTION.

        """
        train = self.parameters['train'] 
        
        res = self.model.recommend_to_one(train=train, user=user)[0:N]       
        ru = [tum[0] for tum in res] 
        return ru
    
    
# In[]
# 评测指标
def random_split_train_test(data, M, k, seed):
    # 分成M份，选择k
    # 划分训练集和测试集, 每次选择一个子集为测试集，其他K-1个集合为训练集
    train, test = [], []
    random.seed(seed)
    for user, item in data:
        if random.randint(0, M-1) == k:
            test.append([user, item])
        else:
            train.append([user, item])
    return train, test

# In[]
# if __name__ == '__main__':
    
#     # # 减少分快执行代码，变量被覆盖
#     # select_model = input("输入执行的模型：1:ItemCF\n2:LFM:")
#     # if select_model == '1':
        
#     item_cf_model = ItemCFModel(model=ItemCF(7))
#     data = item_cf_model.user_items

#     # In[]
#     user_item = []
#     for user, items in data.items():
#         for item in items:
#             user_item.append((user, item))
#     # In[]
#     train_list, test_list = random_split_train_test(user_item, 3, 1, seed=1)
    
#     train = {}
#     for u, item in train_list:
#         if train.get(u) is None:
#             train[u] = [item]
#         else:
#             train[u].append(item)
    
#     test = {}
#     for u, item in test_list:
#         if test.get(u) is None:
#             test[u] = [item]
#         else:
#             test[u].append(item)
#     item_cf_model.fit(train)

#     # In[]
#     for i in range(11, 20, 3):
#         precision = item_cf_model.precision(train, test, i)
#         print("precision:%0.4f" % (precision))
            
#         ## In[]
#         recall = item_cf_model.recall(train, test, i)
#         print("recall:%0.4f" % (recall))

        
# In[] LFModel
# if __name__ == '__main__':
#     lfmodel = LFModel(LFMRecommend(), limit_num=2000)
#     data = lfmodel.user_items
    
#     user_item = []
#     for user, items in data.items():
#         for item in items:
#             user_item.append((user, item))
#     # In[]
#     train_list, test_list = random_split_train_test(user_item, 3, 1, seed=1)
    
#     train = {}
#     for u, item in train_list:
#         if train.get(u) is None:
#             train[u] = [item]
#         else:
#             train[u].append(item)
    
#     test = {}
#     for u, item in test_list:
#         if test.get(u) is None:
#             test[u] = [item]
#         else:
#             test[u].append(item)
            
#     # In[]
    
#     lfmodel.fit(train, F=15, N=10, alpha=0.10, lambda_=0.05, ntimes=2, hot_rank=100)
    
#     # In[]
#     for i in range(3, 5, 2):
#         precision = lfmodel.precision(train, test, i)
#         print("%s precision:%0.4f" % (i, precision))
        
#     # In[]
#     for i in range(3, 5, 2):
#         recall = lfmodel.recall(train, test, i)
#         print("%s recall:%0.4f" % (i, recall))
    

# In[] ICFModel
if __name__ == '__main__':
    icf = ICF()
    data, items_pool, user_pool = icf.getData(1000) # 生产模式下，用全部数据
    icf_model = ICFModel(model=icf)
    
    
    user_item = []
    for user, items in data.items():
        for item in items:
            user_item.append((user, item))
    # In[]
    train_list, test_list = random_split_train_test(user_item, 3, 1, seed=1)
    
    train = {}
    for u, item in train_list:
        if train.get(u) is None:
            train[u] = [item]
        else:
            train[u].append(item)
    
    test = {}
    for u, item in test_list:
        if test.get(u) is None:
            test[u] = [item]
        else:
            test[u].append(item)
    
    # In[]
    icf_model.fit(train, items_pool, user_pool) # 提前计算
    
    # In[]
    for i in range(3, 10, 2):
        precision = icf_model.precision(train, test, i)
        print("%s precision:%0.4f" % (i, precision))
        
    # In[]
    for i in range(3, 10, 2):
        recall = icf_model.recall(train, test, i)
        print("%s recall:%0.4f" % (i, recall))