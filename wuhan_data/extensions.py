# -*- coding: utf-8 -*-
#
# Author: jimin.huang
#
import logging
import os
from scrapy import signals
from wuhan_data.models.instance import Instance


logger = logging.getLogger(__name__)


class WuhanDataExtension(object):
    '''
        用于创建及追踪实例状态的扩展
    '''

    @classmethod
    def from_crawler(cls, crawler):
        return cls()


class InstanceExtension(object):
    '''
        用于创建及追踪实例状态的扩展
    '''
    error_status = False

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls()

        # Connect extensionension object to signals
        crawler.signals.connect(
            extension.spider_opened,
            signal=signals.spider_opened
        )
        crawler.signals.connect(
            extension.spider_closed,
            signal=signals.spider_closed
        )
        crawler.signals.connect(
            extension.spider_error,
            signal=signals.spider_error
        )
        return extension

    def spider_opened(self, spider):
        '''
            爬虫开启时，创建实例
        '''
        spider.instance_id = Instance.insert(Instance(
            name=os.environ['SCRAPY_JOB'],
            address='',
            service='wuhan_data',
            module='crawler',
            status='running',
        ))

    def spider_closed(self, spider, reason):
        '''
            爬虫关闭时，关闭实例
        '''
        if reason == 'finished' and not self.error_status:
            Instance.update(spider.instance_id, 'status', 'closed')
        else:
            Instance.update(spider.instance_id, 'status', 'error')

    def spider_error(self, failure, response, spider):
        '''
            爬虫发生错误，修改实例状态
        '''
        Instance.update(spider.instance_id, 'status', 'error')
        self.error_status = True
