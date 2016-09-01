# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem
from wuhan_data.models.data import Data
import scrapy
import logging
import arrow


logger = logging.getLogger(__name__)


class WuhanDataPipeline(object):
    def process_item(self, item, spider):
        data = Data(
            scrape_time=arrow.now().format('YYYY-MM-DD'),
            name=item['name'],
            source=item['source'],
            checksum=item['checksum'],
            filetype=item['filetype'],
            url=item['url'],
            status=item['status'],
            filepath=item['filepath'],
            public_time=item['public_time'].split('T')[0]
        )
        Data.insert(data)
        return item


class WuhanDataDownloadFilePipeline(FilesPipeline):
    '''
        用于下载文件
    '''
    download_url = (
        'http://www.wuhandata.gov.cn/whdata/resources_resourceDownload.action?'
        'id={id}'
    )
    allowed_filetype = [
        'xlsx', 'pdf'
    ]

    def get_media_requests(self, item, info):
        '''
            重载函数，用于生成下载文件的url及请求
        '''
        item['url'] = self.download_url.format(id=item['id'])
        if item['filetype'] not in self.allowed_filetype:
            raise DropItem()
        yield scrapy.Request(
            item['url'],
            meta={
                'filetype': item['filetype']
            }
        )

    def item_completed(self, results, item, info):
        '''
            重载函数，下载文件完成后的操作
        '''
        # 获取下载的状态作为item的status属性
        item['status'] = 'success' if results[0][0] else 'failed'

        # 获取下载的路径作为item的filepath属性
        # 如果status为failed则为空
        item['filepath'] = results[0][1]['path'] \
            if item['status'] == 'success' else None

        # 获取下载文件的校验和作为item的checksum属性
        # 如果status为failed则为空
        item['checksum'] = results[0][1]['checksum'] \
            if item['status'] == 'success' else None
        return item

    def file_path(self, request, response=None, info=None):
        filename = super(
            WuhanDataDownloadFilePipeline, self
        ).file_path(
            request, response=response, info=info
        ).split('.')[:-1]
        filename = ''.join(filename)
        return '.'.join([filename, request.meta['filetype']])
