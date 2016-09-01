# -*- coding: utf-8 -*-
#
# Author: jimin.huang
#
import logging
import os
from scrapy import signals
from wuhan_data.models.instance import Instance
from wuhan_data.models.crawler_wuhan_data import CrawlerWuhanData
from wuhan_data.config import Config
from wuhan_data.email_sender import EmailSender


logger = logging.getLogger(__name__)


class WuhanDataExtension(object):
    '''
        用于创建及追踪实例状态的扩展
    '''
    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls(crawler.stats)
        crawler.signals.connect(
            extension.item_dropped,
            signal=signals.item_dropped
        )
        crawler.signals.connect(
            extension.spider_opened,
            signal=signals.spider_opened
        )
        crawler.signals.connect(
            extension.item_scraped,
            signal=signals.item_scraped
        )
        crawler.signals.connect(
            extension.spider_closed,
            signal=signals.spider_closed
        )
        return extension

    def spider_opened(self, spider):
        '''
            爬虫开启时记录对应项
        '''
        self.stats.set_value(
            'drop_item_count',
            0
        )
        self.stats.set_value(
            'failed_file_count',
            0
        )

    def item_dropped(self, item, response, exception, spider):
        '''
            爬虫丢弃item时，增加drop_item_count
        '''
        self.stats.inc_value('drop_item_count')

    def item_scraped(self, item, response, spider):
        '''
            爬虫爬取到item时，增加下载文件失败的failed_file_count
        '''
        if item['status'] != 'success':
            self.stats.inc_value('failed_file_count')

    def spider_closed(self, spider, reason):
        '''
            爬虫关闭时写入数据库爬虫状态并发送邮件
        '''
        CrawlerWuhanData.insert(
            CrawlerWuhanData(
                instance_id=spider.instance_id,
                start_time=self.stats.get_value('start_time'),
                finish_time=self.stats.get_value('finish_time'),
                item_scraped_count=self.stats.get_value('item_scraped_count'),
                file_count=self.stats.get_value('file_count'),
                file_status_count_uptodate=self.stats.get_value(
                    'file_status_count/uptodate'
                ),
                drop_item_count=self.stats.get_value('drop_item_count'),
                failed_file_count=self.stats.get_value('failed_file_count'),
            )
        )
        _config = Config('email.yml')
        email_sender = EmailSender.from_config(_config.email)
        email_sender.send_info_mail(
            _config.info_email,
            'Crawler {0} finished'.format(
                spider.name
            ),
            '\n'.join((
                'Stats:',
                'instance_id: {instance_id}',
                'start_time: {start_time}',
                'finish_time: {finish_time}',
                'item_scraped_count: {item_scraped_count}',
                'file_count: {file_count}',
                'file_status_count/uptodate: {file_status_count_uptodate}',
                'drop_item_count: {drop_item_count}',
                'failed_file_count: {failed_file_count}', 
            )).format(
                instance_id=spider.instance_id,
                start_time=self.stats.get_value('start_time'),
                finish_time=self.stats.get_value('finish_time'),
                item_scraped_count=self.stats.get_value('item_scraped_count'),
                file_count=self.stats.get_value('file_count'),
                file_status_count_uptodate=self.stats.get_value('file_status_count/uptodate'),
                drop_item_count=self.stats.get_value('drop_item_count'),
                failed_file_count=self.stats.get_value('failed_file_count'),
            )
        )


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
