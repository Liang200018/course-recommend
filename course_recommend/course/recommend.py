# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 16:13:53 2022

@author: hzsdl
"""

import math
import copy
from course.models import Course, User, UserCourse
 
class ItemCF:
    
    # 获取数据库的数据
    users = User.objects.all().values_list("u_id", flat=True)
    courses = Course.objects.all().values_list("course_id", "name")
    courses_id_name = {course['id']: course['name'] for course in courses} # 用户id和name的dict,{id1: '计算机组成原理'}

    
    train = [] 
    W = [] # 物品归一化矩阵
    users_pool = users  #用户集合
    items_pool = [c['course_id'] for c in courses] #候选项集合
    
    def __init__(self, K):
        self.K = K # 选择
    
    def get_data_from_db(self):
        user_course = UserCourse.objects.filter(state=True).values('user', 'course')
        print(user_course)
        return user_course
        
    
    def write_data_to_db(self):
        
        pass
    
        
    def get_user_items(self):
        # {id: [course1, course2......]}
        user_items = {}
        user_course = self.get_data_from_db()
        for user, course in user_course.items():
            if user_items.get(user) is None:
                user_items[user] = [course]
            else:
                user_items[user].append(course)
        return user_items
    
    
    def ItemSimilarity(self, train):
        # 相似度：N(i)∩N(j)
        #         ---------
        #        N(i)* N(j) 开方
        # train 的格式和user_items相同
    
        
        # 用户倒排表
        N = {item: 0 for item in self.items_pool}
        
        # 根据用户倒排表计算相似度矩阵
        C = {item: {j: 0 for j in self.items_pool} for item in self.items_pool} # 共现矩阵
        W = {item: {j: 0 for j in self.items_pool} for item in self.items_pool} # 相似度矩阵
    
        for user, items in self.train.items():
            for i in items:
                N[i] += 1            
                
                for j in items:
                    if i != j:
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
    
    def recommend_to_one(self, train, user, W, K):
        # 对用户推荐，用户已选择物品的最相似的K个物品
        # 用户的相似度可以理解为喜欢A的同时喜欢B
        # 可以加上选择的理由
        rank = {} # ruj = ∑rui * Wij, i∈S(u)
        user_item_set = train[user] # 注意数据中可以包括显性数据和隐性数据
        # for i, pi in user_item_set.items():
        for i, pi in zip(train[user], [1] * len(train[user])):
            for j, wj in sorted(W[i].items(), key=lambda d: d[1], reverse=True)[0: K]: # rij为物品i与j的相关系数
                # if j not in rank.keys():
                if self.courses_id_name[j] not in rank.keys():
                    # rank[j] = {'weight': 0, 'reason': []}
                    rank[self.courses_id_name[j]] = {'weight': 0, 'reason': []}
                    
                else:
                    # rank[j]['weight'] += pi * wj
                    # rank[j]['reason'].append(i)
                    rank[self.courses_id_name[j]]['weight'] += pi * wj
                    rank[self.courses_id_name[j]]['reason'].append(self.courses_id_name[i])
        return {item: wh_reason for item, wh_reason in rank.items() if wh_reason['weight'] > 0} # K个相关
        
    def recommend_to_all(self):
        pass
    