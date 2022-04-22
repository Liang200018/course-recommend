# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 13:44:48 2022
过滤html经过django转义后的字符
@author: hzsdl
"""

import re

from django import template

register = template.Library()

template.Library()

@register.filter(name='replace_html_escape', is_safe=True)
def replace_html_escape(value):
    """去除经过django转义后的html标签
    """
    try:
        if not isinstance(value, str):
            value = str(value)
        
        if value is not None:
            escape_pattern = r"&[a-zA-Z0-9]*?;"
            s = re.sub(escape_pattern, '', value, flags=re.M) # 多行模式
            maskup_pattern = r"<.*?>"
            s = re.sub(maskup_pattern, '', s, flags=re.M)
            
            # 清楚其他的字符
            res = re.sub(r'[& ]', '', s, flags=re.M)
            return res
        else:
            return ''
    except Exception as e:
        print(e.args)