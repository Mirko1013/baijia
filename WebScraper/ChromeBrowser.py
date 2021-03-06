#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/14 15:52
# @Author  : mirko
# @FileName: ChromeBrowser.py
# @Software: PyCharm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from WebScraper.JsUtils import *
from WebScraper.DataExtractor import DataExtractor

from lxml import etree
from lxml.cssselect import CSSSelector
from pyquery import PyQuery as pq


import threading
import logging

logger = logging.getLogger(__name__)

class ChromeBrowser(object):

    _instance_lock = threading.Lock()

    def __init__(self, path, options, **kwargs):
        self.options = self.chrome_options(options)
        self.browser = webdriver.Chrome(executable_path=path, chrome_options=self.options)


    def chrome_options(self, options):
        default_options = Options()

        for option in options:
            default_options.add_argument(option)

        #手机浏览器配置
        # emulation = {
        #     'deviceName': 'iPhone 6 Plus'
        # }
        #
        # default_options.add_experimental_option("mobileEmulation", emulation)

        #default_options.add_argument('--headless')
        default_options.add_argument('--disable-gpu')
        default_options.add_argument('--no-sandbox')
        default_options.add_argument('blink-settings=imageEnabled=false')
        default_options.add_argument('--disable-plugins')

        return default_options

    def quit(self):
        self.browser.quit()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ChromeBrowser, "_instance"):
            with ChromeBrowser._instance_lock:
                if not hasattr(ChromeBrowser, "_instance"):
                    ChromeBrowser._instance = object.__new__(cls)
        return ChromeBrowser._instance


    def loadUrl(self, url):
        logger.info("Start to load url: {0}".format(url))
        self.browser.execute_script(WINDOW_OPEN.format(url, '_self'))

    def getResponse(self, url, fail=False):

        pass


    def fetchData(self, url, sitemap, parentSelectorId):

        self.loadUrl(url=url)
        #对当前请求进行封装
        #response = etree.HTML(self.browser.page_source)


        #print(etree.tostring(response))
        #response = etree.parse(self.browser.page_source, etree.HTMLParser())

        parentElement = pq(self.browser.page_source)


        dataExtractor = DataExtractor(self, sitemap, parentSelectorId, parentElement("html")[0])
        results = dataExtractor.getData()

        return results