'''
utils.py 的 test
'''
import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import construct_sql

class SqlMethodsTestCase(unittest.TestCase):
    
    def testConstructSql(self):
        
        self.assertEqual(
            construct_sql('user', ['id', 'name'], 10, 'id in (1, 2)'),
            'select id,name from user where id in (1, 2) limit 10')
        
        self.assertEqual(
            construct_sql('user', [], None, None),
            'select * from user')