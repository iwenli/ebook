#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 11:24:56
LastEditors: iwenli
LastEditTime: 2020-12-08 18:09:55
Description: 异常
'''
__author__ = 'iwenli'


class NotDownloadChapterException(Exception):
    """
    没有下载章节异常
    """
    def __init__(self, chapter):
        self.chapter = chapter

    def __str__(self):
        return f"书籍 {self.chapter.BookId} 的章节 {self.chapter.SerialNums} 没有下载"