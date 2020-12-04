#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 11:53:12
LastEditors: iwenli
LastEditTime: 2020-12-01 16:25:50
Description: 数据库操作实体
'''
__author__ = 'iwenli'

from utils.config import conf
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy.sql.sqltypes import Boolean
import sys
import os
sys.path.append(os.path.abspath("."))

# ? sqlalchemy 中文文档 https://www.osgeo.cn/sqlalchemy/
# ? sqlalchemy 官方文档 https://docs.sqlalchemy.org/en/13/orm/tutorial.html#create-an-instance-of-the-mapped-class
ebook_engine = create_engine(
    conf.dbEbookConStr,
    echo=True,  # 当设置为True时会将orm语句转化为sql语句打印，一般debug的时候可用
    pool_size=8,  # 连接池的大小，默认为5个，设置为0时表示连接无限制
    pool_recycle=60 * 30)  # 设置时间以限制数据库多久没连接自动断开

EBookEntityBase = declarative_base()
EBookSession = sessionmaker(bind=ebook_engine)


class BookTask(EBookEntityBase):
    """
    书籍搜目录
    """
    __tablename__ = "BookTask"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Name = Column(String(200), nullable=True)
    Process = Column(Boolean, nullable=True, default=False)
    AddTime = Column(DateTime, nullable=True)

    def __init__(self, name):
        self.Name = name
        self.AddTime = datetime.datetime.now()

    def __repr__(self):
        return f'<BookTask {self.Name}>'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.Name == other.Name


class Book(EBookEntityBase):
    """
    书籍
    """
    __tablename__ = "Book"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Name = Column(String(200), nullable=True)
    Author = Column(String(50), nullable=True)
    Desc = Column(String(3000), nullable=True)
    CategoryId = Column(Integer, nullable=True)
    SubCategoryId = Column(Integer, nullable=True)
    Rate = Column(Integer, nullable=True)
    Cover = Column(String(100), nullable=True)
    Status = Column(Integer, nullable=True)
    WordNums = Column(BigInteger, nullable=True)
    Process = Column(Boolean, nullable=True, default=False)
    AddTime = Column(DateTime, nullable=True)
        
    def __init__(self, name, author, desc, id, subId, rate, cover, status,
                 wordNums):
        '''
        status 状态    0未知    1连载    2完本    3暂停
        '''
        self.Name = name
        self.Author = author
        self.Desc = desc
        self.CategoryId = id
        self.SubCategoryId = subId
        self.Rate = rate
        self.Cover = cover

        if ('连载' in status):
            self.Status = 1
        elif ('完本' in status):
            self.Status = 2
        elif ('暂停' in status):
            self.Status = 3
        else:
            self.Status = 0

        self.AddTime = datetime.datetime.now()

        if ('万字' in wordNums):
            self.WordNums = float(wordNums.replace('万字', '')) * 10000
        elif ('字' in wordNums):
            self.WordNums = int(wordNums.replace('字', ''))
        else:
            self.WordNums = int(wordNums)

    def __repr__(self):
        return f'<Book {self.Name},{self.Author},{self.Status},{self.WordNums}>'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.Name == other.Name


class Category(EBookEntityBase):
    """
    分类
    """
    __tablename__ = "Category"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    ParentId = Column(Integer, nullable=True)
    Name = Column(String(50), nullable=True)
    Url = Column(String(200), nullable=True)
    Sex = Column(Integer, nullable=True)
    AddTime = Column(DateTime, nullable=True)

    def __init__(self, sex, name, url, parentId=0):
        self.ParentId = parentId
        self.Name = name
        self.Url = url
        self.Sex = sex
        self.AddTime = datetime.datetime.now()

    def __repr__(self):
        return f'<Category {self.Name},{self.Url}>'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.Name == other.Name and self.Sex == other.Sex


class Chapter(EBookEntityBase):
    """
    章节
    """
    __tablename__ = "Chapter"

    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    BookId = Column(BigInteger, nullable=True)
    SerialNums = Column(Integer, nullable=True)
    Name = Column(String(200), nullable=True)
    WordNums = Column(BigInteger, nullable=True)
    Url = Column(String(200), nullable=False)
    Status = Column(BigInteger, nullable=False)
    AddTime = Column(DateTime, nullable=True)

    def __init__(self, bookId, serialNums, name, url):
        self.BookId = bookId
        self.SerialNums = serialNums
        self.Name = name
        self.AddTime = datetime.datetime.now()
        self.Url = url
        self.Status = 0
        self.WordNums = 0

    def __repr__(self):
        return f'<Chapter [{self.Status}]{self.Name},{self.BookId},{self.SerialNums},{self.Url}>'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.BookId == other.BookId and self.SerialNums == other.SerialNums


if __name__ == "__main__":
    # ! 首次运行先创建表
    # EBookEntityBase.metadata.create_all(ebook_engine)

    ebook_sesson = EBookSession()
    task = ebook_sesson.query(BookTask).filter_by(Process=False).first()
    print(task)
