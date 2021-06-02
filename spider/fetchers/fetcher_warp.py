#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-15 12:29:09
LastEditors: iwenli
LastEditTime: 2021-06-02 12:42:55
Description: 对抓取进行封装
'''
__author__ = 'iwenli'

import sys
import os
sys.path.append(os.path.abspath("."))
from fetchers import zanghaihuatxt
from fetchers import qdh5
from fetchers import xbiquge
from fetchers import a230book
from fetchers import biquge
from fetchers import qidianxs
from db.entities import Chapter
from utils.helpers import file


def get_book(book_name):
    """抓取书籍信息,整合全部站点

    Args:
        book_name ([string]): [书籍名称]
    """
    book = qdh5.get_book(book_name)
    if book is None:
        book = zanghaihuatxt.get_book(book_name)
    if book is None:
        book = xbiquge.get_book(book_name)
    if book is None:
        book = a230book.get_book(book_name)
    if book is None:
        book = biquge.get_book(book_name)
    return book


def get_chapters(book_name):
    """抓取书籍章节,整合全部站点

    Args:
        book_name ([string]): [书籍名称]
    """
    chapters = zanghaihuatxt.get_chapters(book_name)
    if chapters is None:
        chapters = xbiquge.get_chapters(book_name)
    if chapters is None:
        chapters = a230book.get_chapters(book_name)
    if chapters is None:
        chapters = biquge.get_chapters(book_name)
    if chapters is None:
        return
    res = [
        chapter for chapter in chapters
        if chapter['name'] not in ['请假', '请假条', '无更']
    ]
    return res


def get_chapter_content(chapter):
    """获取章节内容,整合全部站点

    Args:
        chapters ([Chapter]): [本地书籍实体 Chapter]
    """
    if (chapter is None):
        return

    if 'qidianxs.com' in chapter.Url:
        return qidianxs.get_chapter_content(chapter)
    if 'zanghaihuatxt.com' in chapter.Url:
        return zanghaihuatxt.get_chapter_content(chapter)
    elif 'xbiquge.la' in chapter.Url:
        return xbiquge.get_chapter_content(chapter)
    elif '230book.com' in chapter.Url:
        return a230book.get_chapter_content(chapter)
    elif 'biquge.com.cn' in chapter.Url:
        return biquge.get_chapter_content(chapter)
    return None


if __name__ == "__main__":
    name = "芝加哥1990"
    # 1.获取书籍信息
    book = get_book(name)
    print(book)

    # 2.获取书籍章节
    chapters = get_chapters(name)
    print(len(chapters))
    print(chapters)

    # 3. 下载章节
    chapter = Chapter(0, 1, "第一章 测试下载章节", chapters[0]["url"])
    print(get_chapter_content(chapter))
