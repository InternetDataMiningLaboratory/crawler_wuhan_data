# -*- coding: utf-8 -*-
#
# Author: Jimin Huang
#
'''
    测试 ``spiders.crawler``
'''
from wuhan_data.spiders.crawler import WuhanDataSpider
from scrapy.http import Request, Response
from nose.tools import assert_equals
import pkg_resources
import mock


def fake_response_from_file(file_name, url=None):
    '''
        创建一个Scrapy 伪造的HTTP response
        文件从测试目录中读取
    '''
    if url is None:
        url = 'http://www.example.com'

    request = Request(url=url)
    response = None
    with open(
        pkg_resources.resource_filename(
            'wuhan_data.conf',
            '{0}'.format(file_name)
        )
    ) as file:
        response = Response(
            url=url,
            request=request,
            body=file.read()
        )
        response.encoding = 'utf-8'
    return response


@mock.patch.object(WuhanDataSpider, 'parse_list_page')
def test_parse_first_request(mock_list):
    '''
        Test ``WuhanDataSpider.parse_first_request``
    '''
    # 假装启动了爬虫
    spider = WuhanDataSpider()

    # 假装返回了一个从list_template.json中读取内容的response
    fake_response = fake_response_from_file('list_template.json')

    # 获取parse_first_request传入response后的生成器
    results = spider.parse_first_request(fake_response)

    # 总页数已知为113页，前112次返回应该为对应2-113页数的列表页请求
    for index in xrange(1, 114):
        result = results.next()
        assert result.url == spider.list_url.format(page_number=index)


def test_generate_data_item():
    '''
        Test ``WuhanDataSpider.generate_data_item``
    '''
    # 构造测试数据
    fake_data = {
        'id': 1,
        'publicDate': 2,
        'name': 3,
        'source': 'wuhan_data',
        'pathForDatabase': '1.1',
    }

    # 假装启动了爬虫
    spider = WuhanDataSpider()

    # 获取方法读入伪装数据后生成的item
    item = spider.generate_data_item(fake_data)

    # 校验item的键值
    for key, value in fake_data.iteritems():
        if 'Date' in key:
            key = 'public_time'
        if 'path' in key:
            key = 'filetype'
            value = '1'
        assert_equals(value, item[key])


@mock.patch.object(WuhanDataSpider, 'generate_data_item')
def test_parse_list_page(mock_gen):
    '''
        Test ``WuhanDataSpider.parse_list_page``
    '''
    # 假装启动了爬虫
    spider = WuhanDataSpider()

    # 假装返回了一个从list_template.json中读取内容的response
    fake_response = fake_response_from_file('list_template.json')

    # 获取parse_list_page读入response后生成的生成器
    results = spider.parse_list_page(fake_response)

    # 应该获得15个item
    for index in xrange(15):
        try:
            results.next()
        except StopIteration:
            assert False

    # 假装返回了一个从list_none.json中读取内容的response
    fake_response = fake_response_from_file('list_none.json')

    # 获取parse_list_page读入response后生成的生成器
    results = spider.parse_list_page(fake_response)

    assert results.next() is None
