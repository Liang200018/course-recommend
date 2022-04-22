# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 09:44:24 2022

@author: hzsdl

!!!!!!!!!!该程序不可全部执行，会造成重复插入的问题,需要分块执行
!!!!!!!!!!数据已经装载，该程序不可以执行

To-do:
    教师表
    教师和学校的对应关系
"""

import pymysql

import datetime
import os
import json
import copy

import numpy as np
import pandas as pd


# path = r"E:\360MoveData\Users\hzsdl\Desktop\MOOCCube"
# entity_path = os.path.join(path, "entities")
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'mysql_course_recommend',
#         'HOST' : '182.92.131.21',
#         'PORT': '3306',
#         'USER': 'root',
#         'PASSWORD': 'Programmerlzy,.2018',
#         'OPTIONS' : { 'charset' : 'utf8mb4' }, 
#         }
# }


# def get_dict_json(filepath, col=None):
#     lines = []
#     info = {} # 保存文件的信息，如columns
#     with open(filepath, encoding='utf-8') as f:
#         s = f.readline()
#         columns = json.loads(s).keys() if s else []
#         if col is None:
#             col = columns
#         elif set(col) <= set(columns):
#             pass
#             # 什么也不做
#         else:
#             raise ValueError('columns:%s not in %s' % (col, columns))
        
#         while len(s.strip()) > 0: # 处理空白行的问题
#             record = json.loads(s)
#             # remove unwanted key
#             unwanted = set(columns) - set(col)
#             for unwanted_key in unwanted: 
#                 del record[unwanted_key]
#             lines.append(record)
#             s = f.readline()
            
#         info['columns'] = [c for c in columns] # 只是为了不输出dict_keys
#         info['col'] = [c for c in col]
#         print("file columns: %s\ndata columns: %s" % (info['columns'], info['col']))
#         return lines
    
    
# class DataManager:
#     def __init__(self, path_info, tables=None):
#         self.tables = tables if tables is not None else {}
#         self._path_info = path_info #(tname, path, cols)
#         self._pull_data(self._path_info) #加载数据
        
#     def getTable(self, tname):
#         # 获得数据
#         if tname not in self.tables.keys():
#             return ValueError("%s not exists" % tname)
#         return self.tables[tname]
    
#     def setTable(self, tname, path, cols):
#         data = get_dict_json(path, cols)
#         self.tables[tname] = data
    
#     def _pull_data(self, path_info):
#         for tname, path, cols in path_info:
#             data = get_dict_json(path, cols)
#             self.tables[tname] = data

# # In[]
# path_info = [
#     ('course', os.path.join(entity_path, "course.json"), ['id', 'name', 'about', 'prerequisites', 'core_id']),
#     ('user', os.path.join(entity_path, "user.json"), ['id', 'name', 'course_order', 'enroll_time']),
#     ('school', os.path.join(entity_path, "school.json"), ['id', 'name', 'about']),
#     ('teacher', os.path.join(entity_path, "teacher.json"), ['id', 'name', 'about']),
# ]

# tm = DataManager(path_info)


# # In[]
# user = tm.getTable('user')
# course = tm.getTable('course')

# # In[]
# # 打开数据库连接
# db = pymysql.connect(host=DATABASES['default']['HOST'],
#                      user=DATABASES['default']['USER'],
#                      password=DATABASES['default']['PASSWORD'],
#                      database=DATABASES['default']['NAME'],
#                      charset = DATABASES['default']['OPTIONS']['charset']
#                     )
# cursor = db.cursor()

# # In[] # 插入user数据
# insert_user_list = []
# for u in user:
#     u_id = u['id'][2:]
#     name = u['name']
#     password = '123456'
#     created_time = datetime.datetime.now()
#     insert_user_list.append((u_id, name, password, created_time))

# insert_user_sql = '''
#     insert into user(u_id, name, password, created_time)
#     values(%s, %s, %s, %s)

# '''
# try:
#    # 执行sql语句
#    cursor.executemany(insert_user_sql, insert_user_list)
#    # 提交到数据库执行
#    db.commit()
   
# except Exception as e:
#    # 如果发生错误则回滚
#    print(e.args)
#    print("插入失败")
#    db.rollback()

# # In[] # 插入course 数据
# insert_course_list = []
# course_set = set()
# max_length = 0
# for c in course:
#     # print(c['id'])
#     c_id = c['id'].split(':')[1] # C_course-v1:QLU+2018122607X+2019_T1
#     course_id = c_id.lower()  # mysql 中不区分大小写
#     length = len(course_id)
#     if length > max_length:
#         max_length = length
#     if course_id in course_set:
#         # print("重复")
#         continue
#     else:
#         # print(course_id)
#         course_set.add(course_id)
#         name = c['name'].strip()
#         about = c['about'].strip()
#         prerequisites = c['prerequisites'].strip()
#         insert_course_list.append((course_id, name, about, prerequisites))

# insert_course_sql = '''
#     insert into course(course_id, name, about, prerequisites)
#     values(%s, %s, %s, %s)

# '''
# try:
#    # 执行sql语句
#    cursor.executemany(insert_course_sql, insert_course_list)
#    # 提交到数据库执行
#    db.commit()
#    print("插入成功")   
# except Exception as e:
#    # 如果发生错误则回滚
#    print(e.args)
#    print(e)
#    print("插入失败")
#    db.rollback()

# # In[] # 插入user_course数据
# kp_col = ['id', 'course_order']
# user_course = [{k: value for k, value in u.items() if k in  kp_col} for u in user ]
# insert_user_course_list = []
# for u_record in user_course:
#     u_id = u_record['id'][2:]
#     course_order = u_record['course_order']
#     # print(u_id)
#     # print(course_order)
#     for c in course_order:
#         c_id = c.split(':')[1] # C_course-v1:QLU+2018122607X+2019_T1
#         course_id = c_id.lower()  # mysql 中不区分大小写
#         # print((u_id, course_id))
#         insert_user_course_list.append((u_id, course_id))

# insert_user_course_sql = '''
#     insert into user_course(user_id, course_id)
#     values(%s, %s)
# '''
# try:
#    # 执行sql语句
#    cursor.executemany(insert_user_course_sql, insert_user_course_list)
#    # 提交到数据库执行
#    db.commit()
#    print("插入成功")   
# except Exception as e:
#    # 如果发生错误则回滚
#    print(e.args)
#    print("插入失败")
#    db.rollback()

# # In[] # 插入学校数据

# school = tm.getTable('school') # S_SWUFEX
# insert_school_list = []
# for sch in school:
#     sch_id = sch['id'][2:].lower()
#     name = sch['name']
#     about = sch['about']
#     insert_school_list.append((sch_id, name, about))

# insert_school_sql = '''
#     insert into school(sch_id, name, about)
#     values(%s, %s, %s)

# '''
# try:
#    # 执行sql语句
#    cursor.executemany(insert_school_sql, insert_school_list)
#    # 提交到数据库执行
#    db.commit()
#    print("插入成功")
   
# except Exception as e:
#    # 如果发生错误则回滚
#    print(e.args)
#    print("插入失败")
#    db.rollback()
   
# # In[]
# # 关闭数据库连接
# db.close()