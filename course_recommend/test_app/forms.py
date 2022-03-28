# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 17:10:22 2022

@author: hzsdl
"""
from django import forms

class NameForm(forms.Form):
    name = forms.CharField(label="Your Name", max_length=100)