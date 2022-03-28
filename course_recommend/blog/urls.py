# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 09:48:40 2022
@author: hzsdl
将url和视图函数连接起来
"""

from django.conf.urls import include
from django.urls import re_path, path

from django.contrib import admin

urlpatterns = [
            path(r'^admin/', admin.site.urls),] 