#!/usr/bin/env python
'''
Author: iwenli
License: Copyright © 2020 iwenli.org Inc. All rights reserved.
Github: https://github.com/iwenli
Date: 2020-11-30 10:41:59
LastEditors: iwenli
LastEditTime: 2020-12-15 12:47:43
Description: 网络请求
'''
__author__ = 'iwenli'

import requests
from retrying import retry
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.config import Conf


class Http(object):
    """
    一个发送网络请求的简单封装
    """
    conf = Conf()
    ua = UserAgent()
    proxy = []

    def get_proxys():
        # return ['167.172.155.217:8080']
        res = requests.get('{}get_all/'.format(
            Http.conf.httpProxyBaseUrl)).json()
        ret = []
        for item in res:
            ret.append(item.get('proxy'))
        return ret

    def delete_proxy(proxy):
        requests.get("{}delete/?proxy={}".format(Http.conf.httpProxyBaseUrl,
                                                 proxy))

    def __init__(self, useproxy=False, ips=[]):

        self.useproxy = useproxy
        if (useproxy):
            if len(ips) > 0:
                self.proxy = ips
            else:
                self.proxy = Http.get_proxys()

    def check_proxy(self, url):
        """[对指定站点检查代理]
        """
        ips = []
        total = len(self.proxy)
        for index, ip in enumerate(self.proxy):
            try:
                proxies = {'http': ip, 'https': ip}
                print(f"[{index}/{total}] {ip}")
                response = requests.get(url, proxies=proxies, timeout=2)
                if response.status_code == 200 and '小说' in response.text:
                    ips.append(ip)
            except Exception:
                pass
        print(ips)

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

    def get_beautifulsoup(self, url, encoding='utf-8'):
        text = self.get_text(url, encoding)
        return BeautifulSoup(text, 'html.parser')


if __name__ == "__main__":
    __IP_POOL = [
        '120.232.150.110:80', '116.117.134.134:81', '188.113.190.7:80',
        '218.59.139.238:80', '62.84.70.130:80', '60.246.7.4:8080',
        '116.117.134.134:9999', '113.214.13.1:1080', '180.250.12.10:80'
    ]
    http = Http(True, __IP_POOL)
    res = http.check_proxy('http://www.xbiquge.la/')
    print(res)