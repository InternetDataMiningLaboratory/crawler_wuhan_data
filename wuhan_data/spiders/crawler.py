# -*- coding: utf-8 -*-
#
# Author: Jimin Huang
#
'''
    爬取武汉数据
'''
import scrapy
import logging
import arrow
import json
from scrapy.loader.processors import TakeFirst


logger = logging.getLogger(__name__)


class WuhanDataSpider(scrapy.spiders.Spider):
    '''
        爬虫类
    '''
    # 爬虫名字
    name = 'wuhan_data'

    # 允许访问的网站域
    allowed_domains = [
        'wuhandata.gov.cn',
    ]

    # 列表页网址模板
    list_url = (
        'http://www.wuhandata.gov.cn/whdata/resources_list.action?'
        'category=&sortModel=&dataShape=&dataType=&'
        'dataFormat=&publicDateFilter=&'
        'pageNum={page_number}'
    )

    def start_requests(self):
        '''
            构造爬虫开始爬取的请求
        '''
        return scrapy.Request(
            self.list_url.format(page_number=1),
            callback=self.parse_first_request
        )

    def parse_first_request(self, response):
        '''
            解析第一页的请求，获取总页数并发出剩余列表页请求
        '''
        # json格式加载为python对象 
        first_page = json.loads(response.body)

        # 解析总页数
        page_numbers = first_page.get('lastPage', 0)

        # 根据总页数，构造剩余列表页json的请求
        for page_number in xrange(1, page_numbers):
            yield scrapy.Request(
                self.list_url.format(page_number=page_number+1),
                callback=self.parse_list_page
            )

        yield self.parse_list_page(response)

    def parse_list_page(self, response):
        '''
            解析列表页json，获取数据对应id，并生成数据下载url
        '''
        pass
