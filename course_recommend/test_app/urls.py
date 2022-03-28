# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 11:09:23 2022

@author: hzsdl
"""

from django.urls import path, re_path, include
from . import views
from . import forms

urlpatterns = [
    path('hello', views.hello),
    path('form', views.get_name),

    ]


