# -*- coding: utf-8 -*-
# @Time    : 5/25/23 4:26 PM
# @Author  : LIANYONGXING
# @FileName: __init__.py.py

from .stringPreprocessUtils import StringPreprocessUtils

preprocess = StringPreprocessUtils()
keep_ch_only = preprocess.keep_ch_only
keep_ch_en_num = preprocess.keep_ch_en_num
