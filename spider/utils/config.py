#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 11:24:56
LastEditors: iwenli
LastEditTime: 2021-06-02 11:25:37
Description: ...
'''
__author__ = 'iwenli'

from pyiwenli.handlers import ConfigHandler
from pyiwenli.core import LazyProperty
import platform
import socket


class Conf(ConfigHandler):
    '''
    配置
    '''
    @LazyProperty
    def version(self):
        return "1.0.0"

    @LazyProperty
    def autor(self):
        return "iwenli"

    @LazyProperty
    def dbEbookConStr(self):
        '''
        ebook数据库串
        '''
        return 'mysql+pymysql://ebook:zyl521+db@152.136.211.52/ebook?charset=utf8'
        # ConfigHandler.from_env(
        #     "ebook_db_conf",
        #     'mysql+pymysql://username:paaword@0.0.0.0/database?charset=utf8')

    @LazyProperty
    def httpProxyBaseUrl(self):
        '''
        http 代理获取地址
        '''
        return ConfigHandler.from_env("http_proxy_base_url",
                                      'http://proxy.iwenli.org/')

    @LazyProperty
    def picBedServer(self):
        '''
        图床地址
        '''
        return ConfigHandler.from_env("pic_bed_url", 'upload.imageserver.com/')

    @LazyProperty
    def emailPassword(self):
        '''
        email 口令密码
        '''
        return ConfigHandler.from_env("email_pwd", "")

    @LazyProperty
    def emailTo(self):
        '''
        email 收件人列表,多个逗号分隔
        '''
        return ConfigHandler.from_env("email_to",
                                      "ebook@iwenli.org").split(",")

    @LazyProperty
    def platform(self):
        '''
        获取操作系统名称及版本号
        '''
        return platform.platform()

    @LazyProperty
    def hostname(self):
        '''
        获取计算机名称
        '''
        return socket.gethostname()

    @LazyProperty
    def ip(self):
        '''
        获取本机IP
        '''
        return socket.gethostbyname(self.hostname)


conf = Conf()

if __name__ == "__main__":
    cfg1 = Conf()
    cfg2 = Conf()
    import operator
    print(operator.eq(cfg1, cfg2))
    print(cfg1.dbEbookConStr)
    print(cfg1.httpProxyBaseUrl)
