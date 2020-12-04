#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-01 15:44:04
LastEditors: iwenli
LastEditTime: 2020-12-04 15:32:06
Description: 缓存
'''
__author__ = 'iwenli'

from db.entities import EBookSession, Category, Book


class CacheContext(object):
    """
    缓存
    """

    # 当前已经存在的分类List
    categories_cache = None
    # 当前已经存在的分类名称 set
    category_names_cache = None
    # 已经存在的全部书籍名称 set
    book_names_cache = None

    def __init__(self):
        self.refresh()

    def refresh(self):
        """刷新缓存
        """
        ebook_sesson = EBookSession()
        CacheContext.book_names_cache = set(
            [book.Name for book in ebook_sesson.query(Book.Name).all()])
        CacheContext.categories_cache = ebook_sesson.query(Category).all()
        CacheContext.category_names_cache = set(
            [c.Name for c in CacheContext.categories_cache])
        ebook_sesson.close()

    def exists_book(self, book_name):
        """判断书籍是否存在，不存在同时添加到缓存中
        
        Args:
            book_name ([string]): [书籍名称]

        Returns:
            [Bool]: [是否存在]
        """
        if book_name in CacheContext.book_names_cache:
            return True
        CacheContext.book_names_cache.add(book_name)
        return False

    def exists_category(self, category_name):
        """判断分类是否存在，不存在同时添加到缓存中
        
        Args:
            category_name ([string]): [分类名称]

        Returns:
            [Bool]: [是否存在]
        """
        if category_name in CacheContext.category_names_cache:
            return True
        CacheContext.category_names_cache.add(category_name)
        return False

    def get_category(self, category_name):
        """获取分类
        
        Args:
            category_name ([string]): [分类名称]

        Returns:
            [Category]: [分类DB信息]
        """
        for category in CacheContext.categories_cache:
            if category.Name == category_name:
                return category

    def get_all_category(self):
        """获取所有分类

        Returns:
            [List<Category>]: [分类DB信息集合]
        """
        return CacheContext.categories_cache


cacheContext = CacheContext()

if __name__ == "__main__":
    print(cacheContext.exists_book('诛仙'))
    print(cacheContext.category_names_cache)
