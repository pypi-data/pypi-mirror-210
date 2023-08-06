# -*- coding: utf-8 -*-
# @Time    : 5/25/23 4:27 PM
# @Author  : LIANYONGXING
# @FileName: stringPreProcessUtils.py

import re

class StringPreprocessUtils:

    def keep_ch_only(self, text):
        """
        字符串只保留中文
        :param text:
        :return:
        """
        return re.sub(r'[^\u4e00-\u9fa5]', '', text).lower()

    def keep_ch_en_num(self, text, lowercase=True):
        """
        字符串只保留中文和英文字母、数字
        :param text:
        :param lowercase:
        :return:
        """
        if lowercase:
            return re.sub(r'[^0-9a-zA-Z\u4e00-\u9fa5]', '', text).lower()  # 去除除了汉字大小写
        else:
            return re.sub(r'[^0-9a-zA-Z\u4e00-\u9fa5]', '', text)  # 去除除了汉字大小写
