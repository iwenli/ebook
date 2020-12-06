#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 11:49:50
LastEditors: iwenli
LastEditTime: 2020-12-05 20:45:45
Description: 书籍本地操作帮助类
'''
__author__ = 'iwenli'

import re
import os
import sys


class Convert(object):

    CN_NUM = {
        '〇': 0,
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '零': 0,
        '壹': 1,
        '贰': 2,
        '叁': 3,
        '肆': 4,
        '伍': 5,
        '陆': 6,
        '柒': 7,
        '捌': 8,
        '玖': 9,
        '貮': 2,
        '两': 2,
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9
    }

    CN_UNIT = {
        '十': 10,
        '拾': 10,
        '百': 100,
        '佰': 100,
        '千': 1000,
        '仟': 1000,
        '万': 10000,
        '萬': 10000,
        '亿': 100000000,
        '億': 100000000,
        '兆': 1000000000000,
    }

    def chinese_to_arabic(self, cn):
        unit = 0  # current
        ldig = []  # digest
        for cndig in reversed(cn):
            if cndig in self.CN_UNIT:
                unit = self.CN_UNIT.get(cndig)
                if unit == 10000 or unit == 100000000:
                    ldig.append(unit)
                    unit = 1
            else:
                dig = self.CN_NUM.get(cndig)
                if unit:
                    dig *= unit
                    unit = 0
                ldig.append(dig)
        if unit == 10:
            ldig.append(10)
        val, tmp = 0, 0
        for x in reversed(ldig):
            if x == 10000 or x == 100000000:
                val += tmp * x
                tmp = 0
            else:
                tmp += x
        val += tmp
        return val

    def to_chapter(self, chapter_title):
        '''
        规范的章节 转为 (index,name)
        [第五十三章 ...]
        '''
        r = re.findall("(第(.*?)章)", chapter_title)
        if (r is None or len(r) != 1 or len(r[0]) != 2):
            return
        return (self.chinese_to_arabic(r[0][1]),
                str.strip(chapter_title.replace(r[0][0], '')))


class File(object):
    """
    文件辅助操作
    """
    root_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    download_path = os.path.join(root_path, '_download')
    if not os.path.isdir(download_path):
        os.mkdir(download_path)

    def write_book(self, book_id, serial_nums, txt):
        book_path = os.path.join(self.download_path, str(book_id))
        if not os.path.isdir(book_path):
            os.mkdir(book_path)

        file_name = str(serial_nums) + '.txt'
        file_path = os.path.join(book_path, file_name)

        with open(file_path, 'w+', encoding='utf-8') as f:
            f.write(txt)


convert = Convert()
file = File()

if __name__ == "__main__":
    num = convert.chinese_to_arabic('五百二十3')
    print(num)

    r = convert.to_chapter('第一千四百一十三章 合体！')
    print(r)
