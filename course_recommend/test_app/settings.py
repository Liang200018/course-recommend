# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 10:13:52 2022

@author: hzsdl
"""
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # 确保django.contrib.staticfiles已经添加到settings.INSTALLED_APPS中。
    # user define app
    'test_app',
]