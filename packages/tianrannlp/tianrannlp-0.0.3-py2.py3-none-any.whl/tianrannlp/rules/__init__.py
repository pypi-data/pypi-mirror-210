# -*- coding: utf-8 -*-
# @Time    : 5/25/23 3:32 PM
# @Author  : LIANYONGXING
# @FileName: __init__.py.py

from .stringCheckUtils import StringCheckUtils


checker = StringCheckUtils()
is_all_chinese = checker.is_all_chinese
is_all_english = checker.is_all_english
is_all_numbers = checker.is_all_numbers
