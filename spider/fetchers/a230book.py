#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-15 14:24:30
LastEditors: iwenli
LastEditTime: 2020-12-15 16:06:31
Description: 顶点小说
'''

__author__ = 'iwenli'
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.network import Http
from utils.helpers import file
import urllib
from db.entities import Chapter

http = Http(False)

__base_url = 'https://www.230book.com'


def get_book_sp(book_name):
    """[获取书籍的beautifulsoup对象]

    Args:
        book_name ([string]): [书籍名称]
    """
    url = f'https://m.230book.com/s.php?t=1&keyword={book_name}'
    # 搜索书籍
    sp = http.get_beautifulsoup(url)
    tag_p = sp.find('p', class_="title", text=book_name)
    if (tag_p is None):
        return

    book_url = __base_url + tag_p.parent.get('href')
    return (http.get_beautifulsoup(book_url, 'gbk'), book_url)


def get_book(book_name):
    """抓取书籍信息

    Args:
        book_name ([string]): [书籍名称]
    """
    res = get_book_sp(book_name)
    if res is None:
        return
    book_sp = res[0]

    info = book_sp.find("div", id="info")
    author = info.find("p").string.split("：")[1]
    status = info.find("font", color="red").string
    cover = __base_url + book_sp.find("div", id="fmimg").find("img").get('src')
    desc = book_sp.find("div", id="intro").find_all("p")[0].string
    book = {
        'name': book_name,
        'author': author,
        'category': None,
        'subcategory': None,
        'rate': 0,
        'cover': cover,
        'status': status,
        'wordNums': None,
        'desc': desc
    }
    return book


def get_chapters(book_name):
    """抓取书籍章节

    Args:
        book_name ([string]): [书籍名称]
    """
    res = get_book_sp(book_name)
    if res is None:
        return

    book_sp = res[0]
    book_url = res[1]

    tags = book_sp.find('div', id="list").find_all('a')

    chapters = []
    for a in tags:
        name = a.string
        if name is None:
            name = ''
        chapter = {"name": name, "url": book_url + a.get('href')}
        chapters.append(chapter)
    return chapters


def get_chapter_content(chapter):
    """[获取章节内容]

    Args:
        chapters ([Chapter]): [本地书籍实体 Chapter]
    """
    if (chapter is None):
        return

    if (chapter.Status == 0):
        # 开始缓存文字
        sp = http.get_beautifulsoup(chapter.Url, "gbk")
        content = sp.find(id='content')
        if (content is None):
            return

        # content.div.decompose()
        ebook_txts = content.text.replace('\xa0\xa0\xa0\xa0', '\n')  # 去除特殊字符
        return ebook_txts


if __name__ == "__main__":
    name = "我真的是正派"

    # # 1.获取书籍信息
    # book = get_book(name)
    # print(book)

    # # 2.获取书籍章节
    # chapters = get_chapters(name)
    # print(chapters)

    # 3. 下载章节
    chapter = Chapter(0, 1, "第一章 测试下载章节",
                      "https://www.230book.com/book/17665/4791089.html")
    text = get_chapter_content(chapter)
    print(text)
