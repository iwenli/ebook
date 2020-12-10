#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 11:49:50
LastEditors: iwenli
LastEditTime: 2020-12-08 18:15:09
Description: 书籍本地操作帮助类
'''
__author__ = 'iwenli'

import re
import os
import sys
from zipfile import ZipFile, ZIP_DEFLATED
sys.path.append(os.path.abspath("."))
from utils.config import conf
from pyiwenli.handlers import SendEmailHandler
import datetime
from utils.myexceptions import NotDownloadChapterException


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
    zip_path = os.path.join(root_path, '_zip')

    if not os.path.isdir(download_path):
        os.mkdir(download_path)
    if not os.path.isdir(zip_path):
        os.mkdir(zip_path)

    def write_book(self, book_id, serial_nums, txt):
        book_path = os.path.join(self.download_path, str(book_id))
        if not os.path.isdir(book_path):
            os.mkdir(book_path)

        file_name = str(serial_nums) + '.txt'
        file_path = os.path.join(book_path, file_name)

        with open(file_path, 'w+', encoding='utf-8') as f:
            f.write(txt)

    def zip_book_exists(self, book_id):
        """[压缩数据是否存在]

        Args:
            book_id ([int]): [description]
        """
        zip_path = os.path.join(self.zip_path, f"{book_id}.zip")
        return os.path.exists(zip_path)

    def zip_book(self, book, chapters):
        """[压缩书籍]

        Args:
            book ([Book]): [书籍]
            chapters ([List<Chapter>]): [章节]
        """
        file_name = f"{book.Name}[作者-{book.Author}].txt"
        content = f"{book.Name}\n\n{book.Author} 著\n\n"

        for chapter in chapters:
            content += f"{chapter.Name}\n"
            chapter_path = os.path.join(self.download_path, str(book.Id),
                                        f"{str(chapter.SerialNums)}.txt")
            if os.path.exists(chapter_path) == False:
                raise NotDownloadChapterException(chapter)
            with open(chapter_path, "r", encoding='utf-8') as f:
                content += f.read() + "\n\n"
                f.close()

        book_path = os.path.join(self.zip_path, file_name)
        with open(book_path, "w", encoding='utf-8') as out:
            out.write(content)
            out.close()
        # 压缩
        zip_path = os.path.join(self.zip_path, f"{book.Id}.zip")
        book_zip = ZipFile(zip_path, 'w', ZIP_DEFLATED)
        book_zip.write(book_path, file_name)
        book_zip.close()

        # 删除源txt
        os.remove(book_path)
        return True


convert = Convert()
file = File()

email = SendEmailHandler(password=conf.emailPassword, display="EBOOK爬虫")


def sys_info():
    """[获取系统信息]

    Returns:
        [list]: [系统相关信息]
    """
    return [
        f"操作系统:{conf.platform}", f"主机名称:{conf.hostname}", f"IP:{conf.ip}",
        f"当前时间:{datetime.datetime.now().isoformat()}"
    ]


def send_text_email(subject, text, **kw):
    """[发送文本邮件]

    Args:
        subject ([string]): [邮件主题]
        text ([string]): [邮件内容]
    """
    return email.send_text(conf.emailTo, subject, text, **kw)


def send_html_email(subject, html, **kw):
    """[发送 html 邮件]

    Args:
        subject ([string]): [邮件主题]
        html ([string]): [邮件内容]
    """
    return email.send_html(conf.emailTo, subject, html, **kw)


if __name__ == "__main__":
    num = convert.chinese_to_arabic('五百二十3')
    print(num)

    r = convert.to_chapter('第一千四百一十三章 合体！')
    print(r)

    # send_text_email("爬虫开始运行", "\n".join(sys_info()))
