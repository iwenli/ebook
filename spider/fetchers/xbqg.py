#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-04 15:52:07
LastEditors: iwenli
LastEditTime: 2020-12-11 13:14:58
Description: 新笔趣阁 http://www.xbiquge.la
'''
__author__ = 'iwenli'
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.network import Http
from db.entities import Chapter
from utils.helpers import file

# ! 可以通过network提前检测代理
__IP_POOL = [
    '218.59.139.238:80', '116.117.134.134:9999', '120.232.150.110:80',
    '116.117.134.134:80', '39.106.223.134:80', '113.214.13.1:1080',
    '180.250.12.10:80', '116.117.134.134:8081', '123.13.244.153:9999',
    '62.84.70.130:80', '222.75.0.212:80'
]
http = Http(True, __IP_POOL)


def get_book_sp(book_name):
    """[获取书籍的beautifulsoup对象]

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
    return http.get_beautifulsoup(book_url)


def get_book(book_name):
    """抓取书籍信息

    Args:
        book_name ([string]): [书籍名称]
    """
    book_sp = get_book_sp(book_name)
    if book_sp is None:
        return

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
    book_sp = get_book_sp(book_name)
    if book_sp is None:
        return

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

    # 开始缓存文字
    sp = http.get_beautifulsoup(chapter.Url)
    content = sp.find(id='content')
    if (content is None):
        return
    if content.p is not None:
        content.p.decompose()  # 去除底部广告
    ebook_txts = content.text.replace('\xa0', '')  # 去除特殊字符
    return ebook_txts


if __name__ == "__main__":
    # print(get_book('不败战神杨辰'))
    # print(get_chapters('诛仙'))
    chapter = Chapter(0, 1, "第二章 问讯",
                      "http://www.xbiquge.la/71/71456/28238040.html")
    file.write_book(0, 0, get_chapter_content(chapter))