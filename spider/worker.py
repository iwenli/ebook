#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 txooo.com Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-05 18:55:51
LastEditors: iwenli
LastEditTime: 2020-12-06 20:34:34
Description: 处理书籍内容   简单的生产者模式
'''
__author__ = 'iwenli'

import time
from cache import cacheContext
from queue import Queue
from threading import Thread
from fetchers import qdh5, xbqg
from db.entities import EBookSession, BookTask, Book, Category, Chapter
from pyiwenli.handlers import LogHandler
from pyiwenli.utils import timeit
from utils.helpers import file


class Worker(object):
    """
    完整处理书籍
    """
    __limit = 0
    __book_id = 100

    __thread_num = 5

    __book_queue = Queue(0)
    __chapter_queue = Queue(0)

    def __init__(self, thread_num=5):
        self.log = LogHandler('worker')
        self.__thread_num = thread_num
        self._init_data()
        self._info()

    def _info(self):
        _fix = "全局"
        self.log.info(f"[{_fix}] 线程数：{self.__thread_num}")
        self.log.info(f"[{_fix}] 待处理书籍 ：{self.__book_queue.qsize()}")
        self.log.info(f"[{_fix}] 待处理章节 ：{self.__chapter_queue.qsize()}")

    @timeit('初始化数据')
    def _init_data(self):
        """初始化数据
        """
        _fix = "全局"
        self.log.info(f"[{_fix}] 开始提取数据...")
        session = EBookSession()
        books = session.query(Book).filter(Book.Process == False).filter(
            Book.Id >= self.__book_id).limit(self.__limit).all()
        # chapters = session.query(Chapter).filter(Chapter.Status == 0).limit(
        #     self.__limit).all()
        session.close()

        for book in books:
            self.__book_queue.put(book)
        # for chapter in chapters:
        #     self.__chapter_queue.put(chapter)
        self.log.info(f"[{_fix}] 提取数据完成...")

    def fether_chapter(self, id):
        """获取数据章节信息工作函数

        Args:
            id ([int]): [线程序号]
        """
        fix = f"[获取章节信息(线程{id})]"
        self.log.info(f"{fix} 开始执行")

        session = EBookSession()
        session.expire_on_commit = False  # !对象在commit后取消和session的关联，防止session过期后对象被销毁
        index = 0

        while not self.__book_queue.empty():
            book = self.__book_queue.get()
            index += 1
            msg = f"{fix}[{index}/{self.__book_queue.qsize()}]处理书籍 {book.Name}"
            try:
                chapters = xbqg.get_chapters(book.Name)
                if chapters is None:
                    continue
                total = 0
                for index, chapter in enumerate(chapters):
                    total = index + 1
                    model = Chapter(book.Id, total, chapter['name'],
                                    chapter['url'])
                    # 加入数据库
                    session.add(model)
                    session.commit()

                    # 加入到 queue
                    self.__chapter_queue.put(model)

                if total == 0:
                    continue

                # 更新书籍状态
                session.query(Book).filter(Book.Id == book.Id).update(
                    {"Process": True})
                session.commit()

                self.log.info(f"{msg} ,  提取到章节 {total} 条,已加入待下载任务")

            except Exception:
                self.log.error(f"{msg} 异常", exc_info=True)
                self.__book_queue.put(book)
                self.log.warning(f"{msg} 异常,已经放到任务末尾等待重新执行")

        session.close()
        self.log.info(f"{fix} 执行完成")

    def download_chapter(self, id):
        """下载章节

        Args:
            id ([int]): [线程序号]
        """

        fix = f"[下载章节(线程{id})]"
        self.log.info(f"{fix} 开始执行")

        session = EBookSession()
        index = 0
        while True:
            if not self.__book_queue.empty() and self.__chapter_queue.empty():
                self.log.warning(f"{fix} 队列为空，等待10秒后继续检测...")
                time.sleep(10)  # 没有任务  休息10秒
                continue
            if self.__book_queue.empty() and self.__chapter_queue.empty():
                break

            index += 1
            chapter = self.__chapter_queue.get()
            msg = f"{fix}[{index}/{self.__chapter_queue.qsize()}]下载章节 {chapter.Name}"
            try:
                content = xbqg.get_chapter_content(chapter)
                if content is None:
                    self.__chapter_queue.put(chapter)
                    self.log.warning(f"{msg} 下载内容为空,已经放到任务末尾等待重新执行")
                    continue

                chapter.WordNums = len(content)
                chapter.Status = 1

                # 写入文件
                file.write_book(chapter.BookId, chapter.SerialNums, content)

                # 更新 Chapter
                session.query(Chapter).filter(Chapter.Id == chapter.Id).update(
                    {
                        "WordNums": chapter.WordNums,
                        "Status": chapter.Status
                    })
                session.commit()

                self.log.info(f"{msg} 完成")
                self.__chapter_queue.task_done()
            except Exception:
                self.log.error(f"{msg} 异常", exc_info=True)
                self.__chapter_queue.put(chapter)
                self.log.warning(f"{msg} 异常,已经放到任务末尾等待重新执行")

        session.close()
        self.log.info(f"{fix} 执行完成")

    def run(self):
        """执行任务
        """

        _fix = "全局"
        self.log.info(f"[{_fix}] 初始化线程...")
        # 抓取章节线程 1
        fether_job = Thread(target=self.fether_chapter, args=(1, ))
        fether_job.setDaemon(True)
        fether_job.start()

        self.log.info(f"[{_fix}] 抓取章节线程启动完成...")

        # 防止没有 章节下载
        time.sleep(2)

        # 下载章节使用多线程
        for i in range(self.__thread_num):
            download_job = Thread(target=self.download_chapter, args=(i + 1, ))
            download_job.setDaemon(True)
            download_job.start()

        self.log.info(f"[{_fix}] 下载章节线程启动完成...")

        self.__book_queue.join()
        self.log.info(f"[{_fix}] 抓取章节完成...")

        self.__chapter_queue.join()
        self.log.info(f"[{_fix}] 下载章节完成...")

        self.log.info(f"[{_fix}] 全部完成，退出...")

    # !书籍信息

    def generate_book_model(self, **dic):
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
    def spider_book_info_by_task(self):
        """ 根据 task 抓取 book_info
        """
        _name = '书籍搜索'
        self.log.info(f"[{_name}]模块开始处理")
        session = EBookSession()
        session.expire_on_commit = False
        tasks = session.query(BookTask).filter_by(Process=False).all()
        self.log.info(f"[{_name}]待处理数据 {len(tasks)} 条")
        for task in tasks:
            book_name = task.Name

            if cacheContext.exists_book(book_name) is False:
                # 不存在
                book = qdh5.get_book(task.Name)
                if book is None:
                    continue
                model = self.generate_book_model(**book)

                self.log.info(f"[{_name}]提取到书籍：{book}")
                session.add(model)
                session.commit()

                # 加入到 queue
                self.__book_queue.put(model)

            task.Process = True
        session.commit()
        session.close()
        self.log.info(f"[{_name}]模块处理完成...")

    @timeit('分类书籍提取')
    def spider_book_info_by_category(self):
        """ 根据 category 抓取 book_info
        """

        _name = '分类书籍提取'
        self.log.info(f"[{_name}]模块开始处理")

        session = EBookSession()
        session.expire_on_commit = False
        categories = cacheContext.get_all_category()
        self.log.info(f"[{_name}]分类数量：{len(categories)}")
        for category in categories:
            self.log.info(f"[{_name}]处理分类：{category.Name}")
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
                model = self.generate_book_model(**book)
                model.CategoryId = id
                model.SubCategoryId = subId

                self.log.info(f"[{_name}]提取到书籍：{model}")
                session.add(model)
                session.commit()

                # 加入到 queue
                self.__book_queue.put(model)
            # 一次目录一次提交
            session.commit()
        session.close()
        self.log.info(f"[{_name}]模块处理完成...")


if __name__ == '__main__':
    worker = Worker(10)
    worker.spider_book_info_by_task()
    # worker.spider_book_info_by_category()
    worker.run()
