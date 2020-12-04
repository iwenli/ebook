#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 11:24:56
LastEditors: iwenli
LastEditTime: 2020-11-30 11:56:00
Description: ...
'''
__author__ = 'iwenli'

from pyiwenli.handlers import ConfigHandler
from pyiwenli.core import LazyProperty


class Conf(ConfigHandler):
    '''
    配置
    '''
    @LazyProperty
    def dbEbookConStr(self):
        '''
        ebook数据库串
        '''
        return ConfigHandler.from_env(
            "ebook_db_conf",
            'mysql+pymysql://username:paaword@0.0.0.0/database?charset=utf8')

    @LazyProperty
    def httpProxyBaseUrl(self):
        '''
        http 代理获取地址
        '''
        return ConfigHandler.from_env("http_proxy_base_url",
                                      'http://proxy.iwenli.org/')


conf = Conf()

if __name__ == "__main__":
    cfg1 = Conf()
    cfg2 = Conf()
    import operator
    print(operator.eq(cfg1, cfg2))
    print(cfg1.dbEbookConStr)
    print(cfg1.httpProxyBaseUrl)
