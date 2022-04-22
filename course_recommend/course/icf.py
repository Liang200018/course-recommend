# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 16:10:03 2022
增量更新的ItemCF
@author: hzsdl
"""
# In[1]
import numpy as np
import pandas as pd
import scipy.sparse as sp
import math

from course.utils import Singleton # 单例模式
from course.utils import ItemCombination # 生成物品对
from course.recommend import RetrieveData, ItemCF # 获取数据库数据


# In[2]

class ICF(Singleton):
    
    def __init__(self):
        self.Items = set()
        self.Users = set() 
        self.Int = {} # 共现矩阵
        self.S = {} # 物品相似度
        self.N = {} # 物品的选择人数
        
        self.pairs = [] # 记录需要更新的一对对行列确定的元素
        
    
    def getData(self, limit_num=None):
        '''从数据库获得模型数据'''
        fetcher = RetrieveData()
        fetcher.get_data_from_db(limit_num=limit_num) # 获取到全部数据
        items_set = set()
        users_set = set()
        for user, course in fetcher.user_course:
            users_set.add(user)
            items_set.add(course)
            
            
        items_pool = list(items_set)
        users_pool = list(users_set)
        train = fetcher.get_user_items()
        return (train, users_pool, items_pool) 
        
        
    def prepareCompute(self, items_pool, users_pool, train):
        """加载模型需要的数据
        
        :param items_pool: 物品库
        :type items_poll: List 
        :param users_pool: 用户库
        :param train: 训练数据
        :type train: Dict Key[Str]:Value[List]
        
        :return train Dict
        """
        
        self.Items = set(items_pool)
        self.Users = set(users_pool)
        return train
        
    
    def preCompute(self, train):
        """
        提前计算好共现矩阵和物品相似度矩阵
        """
        
        # self.Int = {} #{item: {} for item in items_pool} # 共现矩阵
        # self.N = {} #{item: 0 for item in items_pool}
        
        item_pair = ItemCombination(2)
        for user, items in train.items():
            
            for item in items:
                self.N.setdefault(item, 0)
                self.N[item] += 1
                
            # all pair of item
            for i, j in item_pair.getPairOfItem(items):
                self.Int.setdefault(i, {})
                self.Int[i].setdefault(j, 0)
                self.Int[i][j] += 1
                
        
        for i, j_item in self.Int.items(): # 对出现过的item计算相似度
            for j in j_item.keys():
                self.S.setdefault(i, {})
                self.S[i].setdefault(j, 0)
                if self.N[i] == 0 or self.N[j] == 0:
                    self.S[i][j] = 0
                else:
                    self.S[i][j] = round(
                        (self.Int[i][j] / (math.sqrt(self.N[i]* self.N[j]) * 1.0)), 4)
                        
                
    def recommend_to_one(self, train=None, user=None):
        """
        Parameters
        ----------
        train : TYPE
            生产环境中不需要.
        user : str
            用户id.
            
        Returns
        -------        
            {id: wh_reason}
            wh_reason: {'weight': , 'reason': }
            或者 {}
            type: List
        """
                

        rank = {} 
        try:
            fetcher = RetrieveData()
            user_item_set = fetcher._select_all(cursor=None, table_name='user_course',
                                         col_list=['course_id'], where='user_id=%s' % (user))
          
            user_item_set = [t[0] for t in user_item_set]
            
            # user_item_set = train[user]  # 模型训练时
        except KeyError as e: # 新增用户没有数据
            print(e.args)
            return []
        
        candidate = set() # 物品，至少有一个历史物品和这样的物品共同被选择
        for history_item in user_item_set:
            if self.Int.get(history_item) is None: # 共现稀疏矩阵中没有
                continue
            for related_item in self.Int[history_item].keys():
                candidate.add(related_item)
        for cand in list(candidate):
            total_weight = 0
            neigb_weight = 0
            rank[cand] = {'weight': 0, 'reason': []}
            for item, w in self.S[cand].items():
                if item in user_item_set:
                    neigb_weight += w
                    rank[cand]['reason'].append(item) 
                total_weight += w
            rank[cand]['weight'] = round(neigb_weight / (total_weight * 1.0), 4)
            

        res = {item: wh_reason for item, wh_reason in rank.items()}
        res = sorted(res.items(), key=lambda x: x[1]['weight'], reverse=True)
        return res
    
    
    def writeToDB(self, userid, item_set):
        """把Ua, Ia写入到数据库中
        
        """
        pass
        
    
    def getActiveItemByUserid(self, userid, item_set):
        """接收会话期间，活跃物品的接口
        
        Parameters
        ----------
        userid : TYPE
            DESCRIPTION.
        item_set : Dict
            会话期间的物品    
        
        Returns
        -------
        item_dict : TYPE
            key：item, value: rating.

        """    
        
        item_dict = item_set
        return item_dict
    
    def isNewItem(self, item):
        return item not in self.Items
    
    def addNewItem(self, item):
        self.Items.add(item)
    
    def addNewUser(self, user):
        self.Users.add(user)
        
    def updateIntByDB(self, items, db_user_items):
        """读取数据库中用户的物品集合，更新共现矩阵
        
        :param items: 会话中的新的物品
        :type items: List
        :param db_user_items: 数据库中更新后，该用户评分的物品
        :type db_user_items: List
        """
        
        pairs = []
        old_items = [item for item in db_user_items if item not in items]
        
        for item in items: # 遍历当前会话物品
            if self.isNewItem(item): 
                self.addNewItem(item) # 添加新物品到物品集
                self.Int[item] = {} # 插入新行
                self.S[item] = {} # 插入新行
                self.N.setdefault(item, 0)
                self.N[item] += 1
                
            for old in old_items:
                pairs.append([item, old])
                pairs.append([old, item])

                self.Int[item].setdefault(old, 0) 
                self.Int[old].setdefault(item, 0)  # 插入新列
                self.Int[item][old] += 1
                self.Int[old][item] += 1
                
        self.pairs = pairs
        
        
    def updateS(self):
        for i, j in self.pairs:
            if self.N[i] == 0 or self.N[j] == 0:
                self.S[i][j] = 0
            else:
                self.S[i][j] = round(
                    (self.Int[i][j] / (math.sqrt(self.N[i]* self.N[j]) * 1.0)), 4) 

        del self.pairs
