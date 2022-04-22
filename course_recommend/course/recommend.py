# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 16:13:53 2022

@author: hzsdl
"""

import math
import os
import sys
import copy
import random
import pymysql

from collections import Counter

from course.utils import construct_sql

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysql_course_recommend',
        'HOST' : '182.92.131.21',
        'PORT': '3306',
        'USER': 'root',
        'PASSWORD': 'Programmerlzy,.2018',
        'OPTIONS' : { 'charset' : 'utf8mb4',}, 
        }
}

class RetrieveData:
    courses_id_name = None # {}
    user_course = None # 临时用于计算user_item
    
    # 候选项集合
    users_pool = []
    items_pool = []
    
    # 打开数据库连接
    conn = pymysql.connect(host=DATABASES['default']['HOST'],
                         user=DATABASES['default']['USER'],
                         password=DATABASES['default']['PASSWORD'],
                         database=DATABASES['default']['NAME'],
                         charset = DATABASES['default']['OPTIONS']['charset']
                        )
    
    def __init__(self):
        pass
    
    def reConnect(self):
        self.conn.ping(reconnect=True) # 如果连接失效，重新连接 

    def _select_all(self, cursor, table_name, col_list=None, limit_num=None, where=None):

        sql = construct_sql(table_name, col_list, limit_num, where)
        print(sql)
        
        res = None
        # try:
        self.reConnect()
        with self.conn.cursor() as cursor: 
            cursor.execute(sql)
            res = cursor.fetchall()
        
        # except Exception as e:
            # print(e.args)
        return res
        
    def get_data_from_db(self, limit_num=None):
        """
        设置类变量
        Returns
        -------
        user_course : TYPE
            DESCRIPTION.

        """
        self.reConnect()
        with self.conn.cursor() as cursor:
            
            # 获取数据库的数据
            users = self._select_all(cursor, 'user', ['u_id'])
            self.users_pool = [tup[0] for tup in users]
            
            
            courses = self._select_all(cursor, 'course', ['course_id', 'name'])
            
            courses = [{
                'course_id': tup[0], 'name': tup[1] } for tup in courses]
            self.items_pool = [c['course_id'] for c in courses] #候选项集合
            
            self.courses_id_name = {course['course_id']: course['name'] for course in courses} # 用户id和name的dict,{id1: '计算机组成原理'}
    
            if limit_num:    
                self.user_course = self._select_all(cursor, 'user_course', ['user_id', 'course_id'],
                                                  limit_num=limit_num)
            else: # 为空时读取全部数据
                self.user_course = self._select_all(cursor, 'user_course', ['user_id', 'course_id'],)            
            

        
    def write_data_to_db(self):
        
        pass
    
    
    def get_user_items(self):
        # {id: [course1, course2......]}
        user_items = {}
        user_course = self.user_course
        for user, course in user_course:
            if user_items.get(user) is None:
                user_items[user] = [course]
            else:
                user_items[user].append(course)
        self.user_items = user_items
        return user_items 
    
    

class ItemCF(RetrieveData):
    
    W = [] # 物品归一化矩阵
    

    
    def __init__(self, K):
        self.K = K # 选择
        
    
    def ItemSimilarity(self, train):
        """
        Parameters
        ----------
        train : {id: [course1, course2......]}
            train 的格式和user_items相同
            
        Returns
        -------
        W : TYPE
            物品相关度矩阵
        """
        # 相似度：N(i)∩N(j)
        #         ---------
        #        N(i)* N(j) 开方
        
        # 用户倒排表
        N = {item: 0 for item in self.items_pool}
        
        # 根据用户倒排表计算相似度矩阵
        C = {item: {j: 0 for j in self.items_pool} for item in self.items_pool} # 共现矩阵
        W = {item: {j: 0 for j in self.items_pool} for item in self.items_pool} # 相似度矩阵
        
        for user, items in train.items():
            for i in items:
                if N.get(i) is None:
                    N.setdefault(i, 0)
                N[i] += 1            
                
                for j in items:
                    if i != j:
                        C.setdefault(i, {})
                        C[i].setdefault(j, 0)
                        C.setdefault(j, {})
                        C[j].setdefault(i, 0)
                        C[i][j] += 1
                        C[j][i] += 1
    
        for i in self.items_pool:
            for j in self.items_pool:
                if i == j:
                    continue
                if N[i] == 0 or N[j] == 0:
                    W[i][j] = 0
                else:
                    W[i][j] = C[i][j] / (math.sqrt(N[i]* N[j]) * 1.0)
        
        # 物品相似度的归一化
        ItemCF.W = W       
        return W 
    
    def recommend_to_one(self, train, user, W, K=None):
        """
        Parameters
        ----------
        train : TYPE
            DESCRIPTION.
        user : str
            用户id.
        W : list[[]]
            物品相关度矩阵.
        K : int
            对用户推荐，用户已选择物品的最相似的K个物品

        Returns
        -------        
            {id: wh_reason}
            wh_reason: {'weight': , 'reason': }
            或者 {}
        """
                
        k = self.K if K is None else K
        # 用户的相似度可以理解为喜欢A的同时喜欢B
        # 可以加上选择的理由
        rank = {} # ruj = ∑rui * Wij, i∈S(u)
        try:
            user_item_set = train[user] # 注意数据中可以包括显性数据和隐性数据
        except KeyError as e: # 用户没有数据
            print(e.args)
            return {}
        
        # for i, pi in user_item_set.items():
        for i, pi in zip(train[user], [1] * len(train[user])):
            
            W.setdefault(i, {}) # 临时处理数据不一致问题
            for j, wj in sorted(W[i].items(), key=lambda d: d[1], reverse=True)[0: k]: # rij为物品i与j的相关系数
                if j not in rank.keys():
                # if self.courses_id_name[j] not in rank.keys():
                    rank[j] = {'weight': 0, 'reason': []}
                    # rank[self.courses_id_name[j]] = {'weight': 0, 'reason': []}
                    
                else:
                    rank[j]['weight'] += pi * wj
                    rank[j]['reason'].append(i)
                    # rank[self.courses_id_name[j]]['weight'] += pi * wj
                    # rank[self.courses_id_name[j]]['reason'].append(self.courses_id_name[i])
        res = {item: wh_reason for item, wh_reason in rank.items() if wh_reason['weight'] > 0} # K个相关
        res = sorted(res.items(), key=lambda x: x[1]['weight'], reverse=True)
        return res
    
    def recommend_to_all(self):
        pass

        

class LFMRecommend(RetrieveData):
    # courses_id_name = None # {}
    # user_course = None # 临时用于计算user_item
    # users_pool, items_pool
    train = None # 需要作为类变量， 来去除推荐列表中的已经看过的
    P, Q = None, None
    
    def __init__(self, ):
        pass
    
    def lazy_init(self, F, N, alpha, lambda_, ntimes=1, hot_rank=20):
        """
        F: 隐特征的个数
        N: 迭代次数
        alpha: 学习率
        lambda_: 正则化惩罚系数
        ntimes: 负样本/正样本的比例
        hot_rank: int 物品前n名算作热门
        """
        self.F = F
        self.N = N
        self.alpha = alpha
        self.lambda_ = lambda_
        self.ntimes = ntimes 
        self.hot_rank = hot_rank
    
    def InitModel(self):
        '''初始化P、Q矩阵
        '''
        P, Q = {}, {}
        for user in self.users_pool:
            tmp = {}
            total = 0
            for i in range(0, self.F):    
                tmp[i] = random.uniform(0, 1)
                total += tmp[i]
            P[user] = {k: v/total for k,v in tmp.items()} # 归一化
        for k in range(0, self.F):
            tmp = {}
            total = 0
            for item in self.items_pool: # 注意这里用的是全部物料库
                tmp[item] = random.uniform(0, 1)
                total += tmp[item]
            Q[k] = {k: v/total for k,v in tmp.items()} # 归一化
        self.P = P
        self.Q = Q
        return P, Q
    

    
    def RandomSelectNagtiveSample(self, user, train):
        """
        对每个用户进行负采样
        需要先get_user_items
        Parameters
        ----------
        items : dict
            用户已经有过行为的集合.

        Returns
        -------
        ret : dict
            每个用户的正负样本.

        """
        ret = {}
        items = train[user] # 列表, 训练集中已经选择过的正样本
        
        # check items 
        if isinstance(items, list):
            for item in items:
                ret[item] = 1
        n = 0
        for i in range(0, len(items) * 3): # 为了确保正负样本数量相似
            item = self.items_pool[random.randint(0, len(self.items_pool)) - 1] #随机选择一个候选项
            if item in ret.keys(): # 已经选择作为负样本，跳过
                continue
            ret[item] = 0
            n += 1
            if n > len(items): #选择和正样本数量相同的负样本
                break
        
        return ret

    def RandomSelectHotNagtiveSample(self, user, train):
        """热门的，且没有过行为的
        对每个用户进行负采样
        需要先get_user_items
        Parameters
        ----------
        items : dict
            用户已经有过行为的集合.

        Returns
        -------
        ret : dict
            每个用户的正负样本.

        """
        ret = {}
        items = train[user] # 列表, 训练集中已经选择过的正样本
        
        if self.__dict__.get('hot') is None: # 
            hot = []
            for user, items in train.items():
                hot.extend(items)
            
            self.hot = Counter(hot) # 热门的物品
        else:
            hot = self.__dict__['hot'] # 直接获得缓存的hot
            
            
        # check items 
        if isinstance(items, list):
            for item in items:
                ret[item] = 1
                
        hot_course = [t[0] for t in self.hot.most_common(self.hot_rank)]
        
        n = 0
        while 1:
            # 为了确保正负样本数量相似
            item = self.items_pool[random.randint(0, len(self.items_pool)) - 1] #随机选择一个候选项
            if item in ret.keys(): # 已经选择作为负样本，跳过
                continue
            
            
            if item in hot_course: # 是热门，且没有被选择
                ret[item] = 0
                n += 1
            elif n > (0.6 * len(hot_course)): 
                # 非热门课程, 但是热门课程数目已经被选择60%
                ret[item] = 0
                n += 1
            else:
                continue
            
            print("the length of items: %s" % len(items))
            print("selected %s negative items" % n)
            
            if (n > self.ntimes * len(items)): 
                #选择负样本策略, 热门物品选择完，或者超过正样本的倍数
                break
        
        return ret
    
    
    def _predict(self, user, item):
        """
        建立好P、Q矩阵后，计算user对item的喜欢
        """
        pui = 0 
        for k, puk in self.P[user].items():
            for i, qki in self.Q[k].items():
                if i == item:
                    pui += puk * qki
                    break # 已经找到k-item的系数
        return pui
    
    def LatentFactorModel(self, user_items, train):
        '''
        user_items: user-items_list pairs
        全部用户和全部item构成的矩阵
        train :dict 训练集中的数据，用于估计矩阵参数
        '''
        
        self.train = train
        alpha = self.alpha
        
        operator = 0
        for i in range(0, self.N):
            for user, items in user_items.items():
                # 注意：需要在所有样本上进行矩阵参数的估计
                if train.get(user) is None: #训练集中没有该数据，跳过
                    continue
                
                
                samples = self.RandomSelectHotNagtiveSample(user, train) # 从训练集中返回正样本和负样本
                for item, rui in samples.items():
                    pui = self._predict(user, item) # 预测用户对物品的选择，0-1之间的某一个数值
                    eui = rui - pui # 误差
                    for k in range(0, self.F):
                        operator += 1
                        self.P[user][k] += alpha * eui * (self.Q[k][item] - self.lambda_ * self.P[user][k])
                        self.Q[k][item] += alpha * eui * (self.P[user][k] - self.lambda_ * self.Q[k][item])
            # 根据学习率不是均匀变化的，迭代计算，减少预测误差
            alpha = alpha * 0.9
            print("Operator: %s" % operator)
            
    def recommend_to_one(self, user, N=10):
        """
        对一个用户的推荐列表, 计算P、Q矩阵的内积
        P 是行和为1， Q是列和为1。P['user'][k]，Q[k]['item']
        
        Parameters
        ----------
        user : str
            DESCRIPTION.
        topN : int, optional
            DESCRIPTION. The default is 10.

        Returns
        -------
        {}
            DESCRIPTION.

        """
        
        rank = {}

            
        for k, puk in self.P[user].items():
            for item, qki in self.Q[k].items():
                seen_items = self.train[user] if self.train.get(user) else []
                
                if item not in seen_items: # 排除看过的课程
                    if item not in rank.keys():
                        rank.setdefault(item, 0)
                    rank[item] += puk * qki
        return sorted(rank.items(), key=lambda d: d[1], reverse=True)[0:N]
    

# if __name__ == '__main__':

# In[]
# item_cf = ItemCF(5)
# item_cf.get_data_from_db()

# # In[]
# user_items = item_cf.get_user_items()
# W = item_cf.ItemSimilarity(train=user_items)
# # In[]

# user = '7001215'
# result = item_cf.recommend_to_one(train=user_items, user=user, W=W)
# print(result)

# In[]

# lfm = LFMRecommend(10, 2, 0.2, 0.02)
# lfm.get_data_from_db()
# user_items = lfm.get_user_items()

# # In[]
# train = 
# lfm.Recommend('', 10)