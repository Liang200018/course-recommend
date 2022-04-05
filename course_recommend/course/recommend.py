# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 16:13:53 2022

@author: hzsdl
"""

import math
import os
import sys
import copy

import pymysql

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
 
class ItemCF:
    
    courses_id_name = None # {}
    user_course = None # 临时用于计算user_item
    
    W = [] # 物品归一化矩阵
    
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
    
    def __init__(self, K):
        self.K = K # 选择
    
    def _select_all(self, cursor, table_name, col_list=None, limit_num=None):
        """
        Parameters
        ----------
        cursor : 
        table_name : 表名
        col_list : list
            字段列表.

        Returns
        -------
        list, 列表中元素为元组
        """
        if col_list:
            col_str = ','.join(col_list)
        else:
            col_str = '*'
        sql = '''select %s from %s''' % (col_str, table_name)
        if limit_num:
            sql = sql +' '  + 'limit %s' % (limit_num)
        print(sql)
        res = None
        # try:
        cursor.execute(sql)
        res = cursor.fetchall()
        
        # except Exception as e:
            # print(e.args)
        return res
        
    def get_data_from_db(self):
        """
        设置类变量
        Returns
        -------
        user_course : TYPE
            DESCRIPTION.

        """
        
        cursor = ItemCF.conn.cursor()
        
        # 获取数据库的数据
        users = self._select_all(cursor, 'user', ['u_id'])
        ItemCF.users_pool = [tup[0] for tup in users]
        
        
        courses = self._select_all(cursor, 'course', ['course_id', 'name'])
        
        courses = [{
            'course_id': tup[0], 'name': tup[1] } for tup in courses]
        ItemCF.items_pool = [c['course_id'] for c in courses] #候选项集合
        
        ItemCF.courses_id_name = {course['course_id']: course['name'] for course in courses} # 用户id和name的dict,{id1: '计算机组成原理'}

        ItemCF.user_course = self._select_all(cursor, 'user_course', ['user_id', 'course_id'],
                                              )
        
        cursor.close()

        
    def write_data_to_db(self):
        
        pass
    
        
    def get_user_items(self):
        # {id: [course1, course2......]}
        user_items = {}
        user_course = ItemCF.user_course
        for user, course in user_course:
            if user_items.get(user) is None:
                user_items[user] = [course]
            else:
                user_items[user].append(course)
        ItemCF.user_items = user_items
        return user_items
    
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