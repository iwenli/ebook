#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2019 txooo.com Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-05 18:55:51
LastEditors: iwenli
LastEditTime: 2020-12-24 13:02:55
Description: 处理书籍内容   简单的生产者模式
'''
__author__ = 'iwenli'

import time
from cache import cacheContext
from queue import Queue
from threading import Thread
from fetchers import qdh5, fetcher_warp
from db.entities import EBookSession, BookTask, Book, Category, Chapter
from pyiwenli.handlers import LogHandler
from pyiwenli.utils import timeit
from utils.helpers import file
from utils.myexceptions import NotDownloadChapterException


class Worker(object):
    """
    完整处理书籍
    """
    def __init__(self):
        self.log = LogHandler('worker')
        self.__book_queue = Queue(0)
        self.__chapter_queue = Queue(0)

    @timeit('初始化数据')
    def __init_data(self, top_book=0, top_chapter=0, fix="[全局]", **kwargs):
        """[初始化数据]

        Args:
            top_book ([int]): [书籍数量]
            top_chapter ([type]): [章节数]
            fix ([string]): [日志前缀]
        """
        bid = 0
        cid = 0
        if 'bid' in kwargs.keys():
            bid = kwargs.get('bid')
        if 'cid' in kwargs.keys():
            cid = kwargs.get('cid')

        self.log.info(
            f"{fix} 开始提取数据[top_book={top_book},top_chapter={top_chapter}]...")
        session = EBookSession()

        if top_book > 0:
            books = session.query(Book).filter(Book.Process == False).filter(
                Book.Id > bid).limit(top_book).all()
            for book in books:
                self.__book_queue.put(book)

        if top_chapter > 0:
            chapters = session.query(Chapter).filter(
                Chapter.Status == 0).filter(
                    Chapter.Id > cid).limit(top_chapter).all()
            for chapter in chapters:
                self.__chapter_queue.put(chapter)

        session.close()
        self.log.info(
            f"{fix} 提取数据完成,书籍[{self.__book_queue.qsize()}],章节[{self.__chapter_queue.qsize()}]..."
        )

    def __fether_chapter(self, id):
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
            msg = f"{fix}[{index}/{self.__book_queue.qsize()}]处理书籍 {book.Id}-{book.Name}"
            try:
                chapters = fetcher_warp.get_chapters(book.Name)
                if chapters is None:
                    continue
                total = 0
                for i, chapter in enumerate(chapters):
                    total = i + 1
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

    def __download_chapter(self, id):
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
            msg = f"{fix}[{index}/{self.__chapter_queue.qsize()}]下载章节 {chapter.BookId}-{chapter.Id}-{chapter.Name}"
            try:
                content = fetcher_warp.get_chapter_content(chapter)
                if content is None or len(content) == 0:
                    if "ErrorCount" not in dir(chapter):
                        chapter.ErrorCount = 0
                    if chapter.ErrorCount >= 3:
                        self.log.error(f"{msg} 重试超过3次任然失败，这就放弃了")
                    else:
                        chapter.ErrorCount += 1
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

    # !书籍信息

    def __generate_book_model(self, **dic):
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
    def __spider_book_info_by_task(self):
        """ 根据 task 抓取 book_info
        """
        fix = '[书籍搜索]'
        self.log.info(f"{fix}开始处理...")
        session = EBookSession()
        session.expire_on_commit = False
        tasks = session.query(BookTask).filter_by(Process=False).all()
        total = len(tasks)
        for i, task in enumerate(tasks):
            book_name = task.Name
            _fix = f"{fix}[{i+1}/{total}] {book_name}"
            self.log.info(f"{_fix} 开始...")
            if cacheContext.exists_book(book_name) is False:
                # 不存在
                book = fetcher_warp.get_book(task.Name)
                if book is None:
                    continue
                model = self.__generate_book_model(**book)

                self.log.info(f"{_fix} 提取到书籍：{book}")
                session.add(model)
                session.commit()

                # 加入到 queue
                self.__book_queue.put(model)

            task.Process = True
        session.commit()
        session.close()
        self.log.info(f"{fix}处理完成...")

    @timeit('分类书籍提取')
    def __spider_book_info_by_category(self):
        """ 【起点】根据 category 抓取 book_info
        """

        fix = "[分类书籍提取]"
        self.log.info(f"{fix} 开始处理...")

        session = EBookSession()
        session.expire_on_commit = False
        categories = cacheContext.get_all_category()
        total = len(categories)
        for i, category in enumerate(categories):
            _fix = f"{fix}[{i+1}/{total}] {category.Id}-{category.Name}"
            self.log.info(f"{_fix} 开始...")
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
                model = self.__generate_book_model(**book)
                model.CategoryId = id
                model.SubCategoryId = subId

                self.log.info(f"{_fix} 提取到书籍：{model}")
                session.add(model)
                session.commit()

                # 加入到 queue
                self.__book_queue.put(model)
            # 一次目录一次提交
            session.commit()
        session.close()
        self.log.info(f"{fix} 处理完成...")

    def __gen_thraed(self, thread_num, target):
        """[创建线程]

        Args:
            thread_num ([int]): [线程数]
            target ([def]): [线程委托函数]
        """
        for i in range(thread_num):
            task = Thread(target=target, args=(i + 1, ))
            task.setDaemon(True)
            task.start()

    def __wait(self, fix):
        """[等待队列任务完成]

        Args:
            fix ([string]): [日志前缀]
        """
        self.__book_queue.join()
        self.log.info(f"{fix} 抓取章节完成...")

        self.__chapter_queue.join()
        self.log.info(f"{fix} 下载章节完成...")

        self.log.info(f"{fix} 全部完成，退出...")

    def run_category_spider_download(self, thread_num=5):
        """[从分类同步下载书籍后走完整流程]
        """
        fix = "[分类]"
        self.log.info(f"{fix} 开始执行...")

        self.__spider_book_info_by_category()
        self.__gen_thraed(1, self.__fether_chapter)
        self.__gen_thraed(thread_num, self.__download_chapter)
        self.__wait(fix)

    def run_task_spider_download(self, thread_num=5):
        """[从搜索下载书籍后走完整流程]
        """
        fix = "[搜索]"
        self.log.info(f"{fix} 开始执行...")

        self.__spider_book_info_by_task()
        self.__gen_thraed(1, self.__fether_chapter)
        self.__gen_thraed(thread_num, self.__download_chapter)
        self.__wait(fix)

    def run_spider_download(self,
                            top_book=1000,
                            top_chapter=1000,
                            thread_num=5,
                            bid=0):
        """[抓取书籍章节 && 下载章节]
        
        Args:
            top_book ([int]):    [提取书籍数量]
            top_chapter ([int]): [提取章节数量]
            thread_num ([int]): [下载线程数]
            bid ([int]): [从id为此值的序号开始取]
        """
        fix = "[获取&下载章节]"
        self.log.info(f"{fix} 开始执行...")
        self.__init_data(top_book, top_chapter, fix, bid=bid)
        self.__gen_thraed(1, self.__fether_chapter)
        self.__gen_thraed(thread_num, self.__download_chapter)
        self.__wait(fix)

    def run_download(self, top_chapter=1000, thread_num=5):
        """[下载章节]

        Args:
            top_chapter ([int]): [提取章节数量]
            thread_num ([type]): [下载线程数]
        """
        fix = "[下载章节]"
        self.log.info(f"{fix} 开始执行...")
        self.__init_data(0, top_chapter, fix)
        self.__gen_thraed(thread_num, self.__download_chapter)
        self.__wait(fix)

    @timeit('抓取分类')
    def run_spider_category(self):
        """【起点】抓取分类
        """
        fix = "[抓取分类]"
        self.log.info(f"{fix}开始执行...")
        categories = qdh5.get_categories()
        self.log.info(f"{fix}抓取到根分类 {len(categories)} 条")
        ebook_sesson = EBookSession()
        for category in categories:
            # 一级分类
            categoryDb = cacheContext.get_category(category['name'])
            if categoryDb is None:
                categoryDb = Category(category['sex'], category['name'],
                                      category['url'])
                self.log.info(f"{fix}添加一级分类：{categoryDb}")
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
                    self.log.info(f"{fix}添加二级分类：{subCategoryDb}")
                    ebook_sesson.add(subCategoryDb)
            ebook_sesson.commit()

        self.log.info(f"{fix}执行完成...")
        ebook_sesson.close()

    def run_book_zip(self, id=0, name=None):
        """[打包书籍]

        Args:
            id ([int]): [id]
            id ([string]): [name]
        """
        fix = f'[打包书籍][{id}-{name}]'

        self.log.info(f"{fix}开始...")
        if id == 0 and name is not None:
            id = cacheContext.get_book_id(name)
        if id == 0:
            return False

        try:
            exists = file.zip_book_exists(id)

            if not exists:
                session = EBookSession()
                book = session.query(Book).filter(Book.Id == id).first()

                if book is None:
                    self.log.info(f"{fix} 不存在书籍")
                    return False
                chapters = session.query(Chapter).filter(
                    Chapter.BookId == id).order_by(Chapter.SerialNums).all()
                res = file.zip_book(book, chapters)
                self.log.info(f"{fix}打包结果：{res}")
                return res

            self.log.info(f"{fix}完成...")
            return True
        except NotDownloadChapterException as ex:
            self.log.error(ex)
            # 开始下载
            self.__chapter_queue.put(ex.chapter)
            self.__download_chapter(-1)
            return False
        except Exception:
            self.log.error(f"{fix}异常", stack_info=True)
            return False

    def clean_book_cover(self):
        """[清洗书籍Cover]
        """
        from utils.network import Http
        http = Http()

        ebook_sesson = EBookSession()
        books = ebook_sesson.query(Book).filter(
            Book.Cover.notlike(f'%{"img.txooo.com"}%')).all()
        for book in books:
            url = http.update_image_by_url(book.Cover)
            if 'img.txooo.com' in url:
                book.Cover = url
                ebook_sesson.commit()


if __name__ == '__main__':
    worker = Worker()
    # # ! 1.同步分类
    # # worker.run_spider_category()

    # # ! 2.分类下载书籍完整信息
    # worker.run_category_spider_download()
    # # worker.run_download(10)
    # print(worker.run_book_zip(1766))

    # worker.run_spider_download(100, 0, 10)
    # worker.run_download(1000, 10)

    # ! 3.清洗书籍封面
    worker.clean_book_cover()