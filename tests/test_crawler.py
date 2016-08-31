# -*- coding: utf-8 -*-
#
# Author: Jimin Huang
#
'''
    测试 ``spiders.crawler``
'''
from wuhan_data.spiders.crawler import WuhanDataSpider
from scrapy.http import Request, Response
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

    # 总页数已知为8页，前七次返回应该为对应2-8页数的列表页请求
    for index in xrange(2, 9):
        result = results.next()
        assert result.url == spider.list_url.format(page_number=index)

    # 最后一次返回将会把当前响应传入到parse_list_page
    result = results.next()
    mock_list.assert_called_with(fake_response)





