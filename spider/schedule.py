#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 15:50:37
LastEditors: iwenli
LastEditTime: 2020-12-04 18:08:53
Description: 调度器
'''
__author__ = 'iwenli'

from cache import cacheContext
from db.entities import EBookSession, BookTask, Book, Category, Chapter
from fetchers import qdh5, xbqg
from pyiwenli.handlers import LogHandler
from pyiwenli.utils import timeit
from utils.helpers import file

log = LogHandler('schedule')


# !分类
@timeit('抓取分类')
def spider_category():
    """抓取分类
    """
    _name = '抓取分类'
    log.info(f"[{_name}]模块开始处理")
    categories = qdh5.get_categories()
    log.info(f"抓取到根分类 {len(categories)} 条")
    ebook_sesson = EBookSession()
    for category in categories:
        # 一级分类
        categoryDb = cacheContext.get_category(category['name'])
        if categoryDb is None:
            categoryDb = Category(category['sex'], category['name'],
                                  category['url'])
            log.info(f"添加一级分类：{categoryDb}")
            ebook_sesson.add(categoryDb)
            ebook_sesson.commit()

        # 二级分类
        subCategories = category["subCategories"]
        for subCategory in subCategories:
            subCategoryDb = cacheContext.get_category(subCategory['name'])
            if subCategoryDb is None:
                subCategoryDb = Category(subCategory['sex'],
                                         subCategory['name'],
                                         subCategory['url'], categoryDb.Id)
                log.info(f"添加二级分类：{subCategoryDb}")
                ebook_sesson.add(subCategoryDb)
        ebook_sesson.commit()

    log.info(f"[{_name}]模块处理完成")
    ebook_sesson.close()
    # cacheContext.refresh()  # 更新缓存


# !书籍信息


def generate_book_model(**dic):
    """将书籍字典转换为DBModel

    Returns:
        [Book]: [DB实体]
    """
    # {
    #     'name': name,
    #     'author': author.replace('\n', ''),
    #     'category': categorys[0],
    #     'subcategory': categorys[1],
    #     'rate': rate,
    #     'cover': cover,
    #     'status': outhers[1],
    #     'wordNums': outhers[0],
    #     'desc': desc
    # }
    id = 0
    subId = 0
    if dic['subcategory'] is not None:
        subcategory = cacheContext.get_category(dic['subcategory'])
        if subcategory is not None:
            id = subcategory.ParentId
            subId = subcategory.Id
    elif dic['category'] is not None:
        category = cacheContext.get_category(dic['category'])
        if category is not None:
            id = category.Id
            subId = 0
    return Book(dic['name'], dic['author'], dic['desc'], id, subId,
                dic['rate'], dic['cover'], dic['status'], dic['wordNums'])


@timeit('书籍搜索')
def spider_book_info_by_task():
    """ 根据 task 抓取 book_info
    """
    _name = '书籍搜索'
    log.info(f"[{_name}]模块开始处理")
    ebook_sesson = EBookSession()
    tasks = ebook_sesson.query(BookTask).filter_by(Process=False).all()
    log.info(f"[{_name}]待处理数据 {len(tasks)} 条")
    for task in tasks:
        book_name = task.Name

        if cacheContext.exists_book(book_name) is False:
            # 不存在
            book = qdh5.get_book(task.Name)
            if book is None:
                continue
            model = generate_book_model(**book)

            log.info(f"[{_name}]提取到书籍：{book}")
            ebook_sesson.add(model)
        task.Process = True
    ebook_sesson.commit()
    ebook_sesson.close()
    log.info(f"[{_name}]模块处理完成...")


@timeit('分类书籍提取')
def spider_book_info_by_category():
    """ 根据 category 抓取 book_info
    """

    _name = '分类书籍提取'
    log.info(f"[{_name}]模块开始处理")

    ebook_sesson = EBookSession()
    categories = cacheContext.get_all_category()
    log.info(f"[{_name}]分类数量：{len(categories)}")
    for category in categories:
        log.info(f"[{_name}]处理分类：{category.Name}")
        subId = category.Id
        id = category.ParentId
        if id == 0:
            id = subId
            subId = 0

        books = qdh5.get_books(category.Url)
        for book in books:
            if cacheContext.exists_book(book['name']) is True:
                continue
            # 不存在
            model = generate_book_model(**book)
            model.CategoryId = id
            model.SubCategoryId = subId

            log.info(f"[{_name}]提取到书籍：{model}")
            ebook_sesson.add(model)
        # 一次目录一次提交
        ebook_sesson.commit()
    ebook_sesson.close()
    log.info(f"[{_name}]模块处理完成...")


# !章节信息


@timeit('抓取章节')
def spider_chapter(top=10):
    """抓取章节
    """
    _name = '分类书籍提取'
    log.info(f"[{_name}]模块开始处理")

    ebook_sesson = EBookSession()
    books = ebook_sesson.query(Book).filter_by(Process=False).limit(top).all()
    log.info(f"[{_name}]本次提取到书籍：{len(books)}")
    for book in books:
        log.info(f"[{_name}]处理书籍 {book.Name}")
        chapters = xbqg.get_chapters(book.Name)
        if chapters is None:
            continue
        models = []
        for index, chapter in enumerate(chapters):
            model = Chapter(book.Id, index + 1, chapter['name'],
                            chapter['url'])
            models.append(model)
            # ebook_sesson.add(model)
        if len(models) > 0:
            ebook_sesson.add_all(models)

        log.info(f"[{_name}]书籍提取到章节 {len(models)} 条")

        book.Process = True
        ebook_sesson.commit()
    ebook_sesson.close()
    log.info(f"[{_name}]模块处理完成...")


@timeit('下载章节')
def download_chapter(top=10):
    """下载章节
    """
    _name = '下载章节'
    log.info(f"[{_name}]模块开始处理")

    ebook_sesson = EBookSession()
    chapters = ebook_sesson.query(Chapter).filter_by(Status=0).limit(top).all()

    log.info(f"[{_name}]提取到待下载章节 {len(chapters)}")
    for chapter in chapters:
        try:
            content = xbqg.get_chapter_content(chapter)
            if content is None:
                continue

            chapter.WordNums = len(content)
            chapter.Status = 1

            # 写入文件
            file.write_book(chapter.BookId, chapter.SerialNums, content)
            ebook_sesson.commit()
            log.info(f"[{_name}]章节下载完成 {chapter}")
        except Exception as ex:
            log.error(f"[{_name}]{chapter}异常 ", ex)

    ebook_sesson.close()
    log.info(f"[{_name}]模块处理完成...")


if __name__ == "__main__":
    # 分类信息
    # spider_category()

    # 书籍信息
    # spider_book_info_by_task()
    # spider_book_info_by_category()

    # 章节信息
    # spider_chapter()

    # 下载章节
    # download_chapter()
    pass