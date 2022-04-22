# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 17:12:37 2022
    LFM模型
    定期执行， 数据量比较大

To-do:
    LFM模型写入MYSql推荐表    
@author: hzsdl
"""

import pymysql
from course.measure import LFModel, random_split_train_test
from course.recommend import LFMRecommend


if __name__ == '__main__':
    
    lfmodel = LFModel(LFMRecommend(F=10, N=100, alpha=0.02, lambda_=0.01))
    data = lfmodel.user_items
    
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
    
    lfmodel.fit(train)
    
    
