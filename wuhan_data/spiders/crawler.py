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
from wuhan_data.items import WuhanDataItem


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
        return [scrapy.Request(
            self.list_url.format(page_number=1),
            callback=self.parse_first_request
        )]

    def parse_first_request(self, response):
        '''
            解析第一页的请求，获取总页数并发出剩余列表页请求
        '''
        # json格式加载为python对象 
        first_page = json.loads(response.body)

        # 解析总页数
        page_numbers = first_page.get('pages', 0)

        # 根据总页数，构造剩余列表页json的请求
        for page_number in xrange(page_numbers):
            yield scrapy.Request(
                self.list_url.format(page_number=page_number+1),
                callback=self.parse_list_page,
                dont_filter=True
            )

    def generate_data_item(self, data):
        '''
            解析数据，得到结构化的Scrapy Item对象
        '''
        # 生成ItemLoader对象 
        item_loader = scrapy.loader.ItemLoader(item=WuhanDataItem())

        # 设置默认输出第一个值
        item_loader.default_output_processor = TakeFirst()

        # 读取数据id
        item_loader.add_value('id', data['id'])

        # 读取数据名称
        item_loader.add_value('name', data['name'])

        # 读取数据发布时间
        item_loader.add_value('public_time', data['publicDate'])

        # 写入数据来源
        item_loader.add_value('source', 'wuhan_data')

        # 读取pathForDatabase用'.'截断的最后一部分作为filetype
        item_loader.add_value(
            'filetype',
            data['pathForDatabase'].split('.')[-1]
        )

        # 返回构造的Item
        return item_loader.load_item()

    def parse_list_page(self, response):
        '''
            解析列表页json，获取数据对应id，并生成数据下载url
        '''
        # json格式加载为python对象
        list_page = json.loads(response.body)

        # 获取该页所有数据
        # 如果没有数据，打印log并结束对该页的解析
        try:
            datum = list_page['list']
        except KeyError:
            logger.error('{page_number} page no data')
            yield None

        # 对于每一个数据解析返回Item对象
        for data in datum:
            yield self.generate_data_item(data)
