#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-04 15:52:07
LastEditors: iwenli
LastEditTime: 2020-12-09 21:53:07
Description: 新笔趣阁
'''
__author__ = 'iwenli'
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.network import Http

http = Http(False)


def get_book(book_name):
    """抓取书籍信息

    Args:
        book_name ([string]): [书籍名称]
    """
    url = 'http://www.xbiquge.la/modules/article/waps.php?searchkey=' + book_name

    # 搜索书籍
    sp = http.get_beautifulsoup(url)
    tag_a = sp.find('a', text=book_name)
    if (tag_a is None):
        return

    book_url = tag_a.get('href')
    book_sp = http.get_beautifulsoup(book_url)
    main = book_sp.find("div", id="maininfo")
    author = main.find("p").string.split("：")[1]
    category = book_sp.find("div", class_="con_top").find_all("a")[2].string
    cover = book_sp.find("div", id="fmimg").find("img").get('src')
    desc = book_sp.find("div", id="intro").find_all("p")[1].string
    book = {
        'name': book_name,
        'author': author,
        'category': category,
        'subcategory': None,
        'rate': 0,
        'cover': cover,
        'status': None,
        'wordNums': None,
        'desc': desc
    }
    return book


def get_chapters(book_name):
    """抓取书籍章节

    Args:
        book_name ([string]): [书籍名称]
    """
    url = 'http://www.xbiquge.la/modules/article/waps.php?searchkey=' + book_name

    # 搜索书籍
    sp = http.get_beautifulsoup(url)
    tag_a = sp.find('a', text=book_name)
    if (tag_a is None):
        return

    # 解析章节
    book_url = tag_a.get('href')
    book_sp = http.get_beautifulsoup(book_url)
    tag_dds = book_sp.find_all('dd')

    chapters = []
    for tag in tag_dds:
        a = tag.find('a')
        name = a.string
        if name is None:
            name = ''
        chapter = {
            "name": name,
            "url": 'http://www.xbiquge.la' + a.get('href')
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
        sp = http.get_beautifulsoup(chapter.Url)
        content = sp.find(id='content')
        if (content is None):
            return

        content.p.decompose()  # 去除底部广告
        ebook_txts = content.text.replace('\xa0\xa0\xa0\xa0', '')  # 去除特殊字符
        return ebook_txts


if __name__ == "__main__":
    # print(get_chapters('斗罗大陆4终极斗罗'))
    print(get_book('不败战神杨辰'))