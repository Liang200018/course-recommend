# -*- coding: utf-8 -*-
"""
@author: hzsdl
"""

import sqlite3


def construct_sql(table_name, col_list=None, limit_num=None, where=None):
    """
    Parameters
    ---------- 
    table_name : 表名
    col_list : list
        字段列表.
    limit_num int 
    where str where子句
    Returns
    -------
    list, 列表中元素为元组
    """
    if col_list:
        col_str = ','.join(col_list)
    else:
        col_str = '*'
    sql = '''select %s from %s''' % (col_str, table_name)
    if where:
        sql = sql + ' ' + 'where %s' % (where)
    if limit_num:
        sql = sql +' '  + 'limit %s' % (limit_num)
        
    return sql



class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls) # 找到父类
            cls._instance = orig.__new__(cls) # 找到
        return cls._instance
    

from itertools import combinations, permutations # 排列组合

class ItemCombination:
    
    def __init__(self, k=2):
        self.k = k

    def getPairOfItem(self, items):
        return permutations(items, self.k)  


    
    
    
    