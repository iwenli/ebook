#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-12-06 12:23:37
LastEditors: iwenli
LastEditTime: 2020-12-17 10:02:47
Description: 入口程序
'''
__author__ = 'iwenli'

import schedule
import click
import time
from utils.helpers import sys_info, send_text_email, email
from pyiwenli.handlers import LogHandler
from worker import Worker
from utils.config import conf
import random
from cache import cacheContext

log = LogHandler('run')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def gen_key():
    return ''.join(random.sample('0123456789zyxwvutsrqponmlkjihgfedcba', 10))


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=conf.version)
def cli():
    """[cli工具]
    """
    print(f"eBook Spider {conf.version} By {conf.autor} ...")


@cli.command(name="spiderDownload")
@click.option("--top", default=100, help='书籍数')
@click.option("--num", default=10, help='下载章节线程数')
@click.option("--bid", default=0, help='从id为多少的序号开始取')
def spiderDownload(top, num, bid=0):
    key = gen_key()
    worker = Worker()
    send_text_email(f"抓取书籍章节 && 下载章节[{key}]-{top}-{num}-{bid}",
                    "\n".join(sys_info()))
    worker.run_spider_download(top, 0, num, bid)
    send_text_email(f"抓取书籍章节 && 下载章节[{key}]-{top}-{num}-{bid}",
                    "\n".join(sys_info()))


@cli.command(name="download")
@click.option("--top", default=10000, help='下载章节数')
@click.option("--num", default=10, help='线程数')
def download(top, num):
    key = gen_key()
    worker = Worker()
    send_text_email(f"开始下载章节[{key}]-{top}-{num}", "\n".join(sys_info()))
    worker.run_download(top, num)
    send_text_email(f"下载章节完成[{key}]-{top}-{num}", "\n".join(sys_info()))


@cli.command(name="zip")
@click.option("--bid", default=0, help='书籍id')
@click.option("--bname", default=None, help='书籍名称')
def zip(bid, bname):
    print(Worker().run_book_zip(bid, bname))


# def job(msg):
#     log.info(msg)

# def run():
#     schedule.every(10).seconds.do(job, "每隔10秒运行一次")
#     schedule.every(1).minutes.do(job, "每隔1分钟运行一次")
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

if __name__ == "__main__":
    cli()
