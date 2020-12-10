#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-04 15:52:07
LastEditors: iwenli
LastEditTime: 2020-12-09 22:36:46
Description: 笔趣阁 https://www.zanghaihuatxt.com/
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


def get_book_sp(book_name):
    """[获取书籍的beautifulsoup对象]

    Args:
        book_name ([string]): [书籍名称]
    """
    url = f'https://so.biqusoso.com/s.php?siteid=zanghaihuatxt.com&ie=utf-8&q={urllib.parse.quote(book_name)}'
    # 搜索书籍
    sp = http.get_beautifulsoup(url)
    tag_a = sp.find('a', text=book_name)
    if (tag_a is None):
        return

    book_url = tag_a.get('href')
    return http.get_beautifulsoup(book_url, "gbk")


def get_book(book_name):
    """抓取书籍信息

    Args:
        book_name ([string]): [书籍名称]
    """
    book_sp = get_book_sp(book_name)
    if book_sp is None:
        return

    info = book_sp.find("div", id="info")
    author = info.find("p").string.split("：")[1]
    status = info.find_all("p")[1].string.split("：")[1]
    cover = "https://www.zanghaihuatxt.com" + book_sp.find(
        "div", id="fmimg").find("img").get('src')
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
    book_sp = get_book_sp(book_name)
    if book_sp is None:
        return

    tag_dds = book_sp.find_all('dd')

    chapters = []
    for tag in tag_dds[12:]:  # 前12个为最新章节
        a = tag.find('a')
        name = a.string
        if name is None:
            name = ''
        chapter = {
            "name": name,
            "url": 'https://www.zanghaihuatxt.com' + a.get('href')
        }
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
        ebook_txts = content.text.replace('\xa0\xa0\xa0\xa0', '')  # 去除特殊字符
        return ebook_txts


if __name__ == "__main__":
    # print(get_book('不败战神杨辰'))
    # print(get_chapters('不败战神杨辰'))
    chapter = Chapter(
        0, 1, "第57章 可怜之人",
        "https://www.zanghaihuatxt.com/11717_11717404/61691315.html")
    file.write_book(0, 0, get_chapter_content(chapter))
