#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 11:52:08
LastEditors: iwenli
LastEditTime: 2020-12-01 15:30:45
Description: 起点H5
'''
__author__ = 'iwenli'
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.network import Http
from urllib import parse

http = Http(False)


def get_categories():
    """
    获取起点书籍分类
    """
    base = 'https://m.qidian.com'  # 主域
    raw_urls = [(1, 'https://m.qidian.com/category/male'),
                (2, 'https://m.qidian.com/category/female')]
    categories = []
    for url_item in raw_urls:

        sex = url_item[0]
        url = url_item[1]

        sp = http.get_beautifulsoup(url)
        categoryTags = sp.select('.sort-li')
        for tag in categoryTags:
            href = tag.select('.sort-li-header')[0].get('href')
            name = tag.select('.module-title')[0].string

            category = {
                "name": name,
                "sex": sex,
                "url": base + href,
                "subCategories": []
            }

            subCategoryTag = tag.find(class_='sort-li-detail').find_all('a')
            for subTag in subCategoryTag:
                subCategory = {
                    "name": subTag.string,
                    "sex": sex,
                    "url": base + subTag.get('href')
                }
                category["subCategories"].append(subCategory)

            categories.append(category)
    return categories


def get_book(book_name):
    '''
    查找书籍
    返回书籍信息
    URL:https://m.qidian.com/search?kw=凡人修仙之仙界篇
    '''
    url = "https://m.qidian.com/search?kw={}".format(book_name)
    bs = http.get_beautifulsoup(url)
    img = bs.find('img', alt=book_name)
    if (img is None):
        return None
    book_url = "https://m.qidian.com{}".format(img.parent.get('href'))
    book_bs = http.get_beautifulsoup(book_url)

    layout = book_bs.find('div', class_='book-layout')
    name = layout.find('h2', class_='book-title').text
    cover = layout.find('img', class_='book-cover').get('src')

    author_tag = layout.find('a', role='option')
    author_tag.aria.decompose()
    author_tag.aria.decompose()  # 移除标签span
    author_tag.span.decompose()  # 移除标签span
    author = author_tag.text

    desc = book_bs.find('section', id='bookSummary').find('content').text

    metas = layout.find_all('p', class_='book-meta')
    categorys = metas[0].text.split('/')
    outhers = metas[1].text.split('|')
    rate = None
    rate_tag = layout.find('span', class_='star-score')
    if rate_tag is not None:
        rate = rate_tag.text
    # category
    book = {
        'name': name,
        'author': author.replace('\n', ''),
        'category': categorys[0],
        'subcategory': categorys[1],
        'rate': rate,
        'cover': cover,
        'status': outhers[1],
        'wordNums': outhers[0],
        'desc': desc
    }
    return book


def get_books(categoryUrl):
    '''
    根据分类 获取 books
    '''
    books = []
    url = categoryUrl
    category_base = 'https://m.qidian.com/majax/category/list'
    csrfToken = http.get_cookie(url, '_csrfToken')

    query = parse.urlsplit(url).query
    # ! https://m.qidian.com/majax/category/list?_csrfToken=5vqRK0lpRXFzdGzvzUXzw310CmQuv9N9Z7Z9KMC6&gender=male&pageNum=2&catId=4&subCatId=6
    for i in range(5):
        page_num = i + 1
        page_url = f'{category_base}?_csrfToken={csrfToken}&{query}&pageNum={page_num}'

        resp = http.get(page_url).json()
        books_json = resp.get('data').get('records')
        for book in books_json:
            # name, author, desc, id, subId, rate, cover, status, wordNums
            bid = book.get('bid')
            book = {
                'name': book.get('bName'),
                'author': book.get('bAuth'),
                'category': None,
                'subcategory': None,
                'rate': None,
                'cover': f'https://bookcover.yuewen.com/qdbimg/349573/{bid}',
                'status': book.get('state'),
                'wordNums': book.get('cnt'),
                'desc': book.get('desc')
            }
            books.append(book)
    return books


if __name__ == "__main__":
    # 1.书籍信息
    book = get_book('诛仙')
    # print(book)

    # # 2.分类信息
    # categories = get_categories()
    # print(categories)

    # # 3.根据分类地址获取分类下的书籍
    # url = 'https://m.qidian.com/category/detail?catId=1&subCatId=201&gender=male'
    # books = get_books(url)
    # print(books)