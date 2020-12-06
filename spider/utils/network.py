#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 10:41:59
LastEditors: iwenli
LastEditTime: 2020-12-05 22:24:03
Description: 网络请求
'''
__author__ = 'iwenli'

from utils.config import Conf
import requests
from retrying import retry
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
import sys
import os
sys.path.append(os.path.abspath("."))


class Http(object):
    """
    一个发送网络请求的简单封装
    """
    conf = Conf()
    ua = UserAgent()
    proxy = []

    def get_proxys():
        res = requests.get('{}get_all/'.format(
            Http.conf.httpProxyBaseUrl)).json()
        ret = []
        for item in res:
            ret.append(item.get('proxy'))
        return ret

    def delete_proxy(proxy):
        requests.get("{}delete/?proxy={}".format(Http.conf.httpProxyBaseUrl,
                                                 proxy))

    def __init__(self, useproxy=False):

        self.useproxy = useproxy
        if (useproxy):
            self.proxy = Http.get_proxys()

    # 最大重试3次，3次全部报错，才会报错,每次重试间隔 2秒-10秒

    @retry(stop_max_attempt_number=3,
           wait_random_min=2000,
           wait_random_max=10000)
    def get_internal(self, url):
        '''
        get请求的出口
        '''
        headers = {'User-Agent': str(Http.ua.random)}

        proxies = None
        if (self.useproxy):
            ip = random.choice(self.proxy)
            proxies = {'http': ip, 'https': ip}
        response = requests.get(url,
                                headers=headers,
                                proxies=proxies,
                                timeout=30)
        # 超时的时候回报错并重试

        # if (response.status_code != 200):
        #     print(f'{url}请求状态{response.status_code}，马上重试')

        assert response.status_code == 200  # 状态码不是200，也会报错
        return response

    def get(self, url):
        return self.get_internal(url)

    def get_text(self, url, encoding='utf-8'):
        try:
            resp = self.get_internal(url)
            resp.encoding = encoding
            return resp.text
        except Exception as ex:
            print(ex)
            return ''

    def get_cookie(self, url, cookie_name):
        response = self.get_internal(url)
        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        cookie = cookies.get(cookie_name)
        return cookie

    def get_beautifulsoup(self, url):
        text = self.get_text(url)
        return BeautifulSoup(text, 'html.parser')


if __name__ == "__main__":
    http = Http(False)
    rep = http.get_text('http://m.qidian.com/book/2019')
    print(rep)