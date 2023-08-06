# -*- coding: utf-8 -*-
# @Time    : 5/25/23 3:33 PM
# @Author  : LIANYONGXING
# @FileName: regulations.py

class StringCheckUtils:
    def __init__(self):
        pass

    def is_all_chinese(self, text):
        """
        判断字符串是否全为中文
        :param text:
        :return:
        """
        for char in text:
            if not self.is_chinese(char):
                return False
        return True

    def is_all_english(self, text):
        """
        判断字符串是否全为英文
        :param text:
        :return:
        """
        for char in text:
            if not self.is_english(char):
                return False
        return True

    def is_all_numbers(self, text):
        """
        判断字符串是否全为数字
        :param text:
        :return:
        """
        for char in text:
            if not self.is_number(char):
                return False
        return True

    def is_number(self, char):
        """
        判断单个字符是否为阿拉伯数字
        :param char:
        :return:
        """
        if not '0' <= char <= '9':
            return False
        return True

    def is_english(self, char):
        """
        判断单个字符是否为英文字母
        :param char:
        :return:
        """
        if not 'A' <= char <= 'Z' and not 'a' <= char <= 'z':
            return False
        return True

    def is_chinese(self, char):
        """
        判断单个字符是否为中文
        :param char:
        :return:
        """
        if u'\u4e00' <= char <= u'\u9fa5':
            return True
        return False
