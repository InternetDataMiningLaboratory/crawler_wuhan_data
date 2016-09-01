# -*- coding: utf-8 -*-
#
# Author: QianfuFinance
#
'''
    ``crawler_wuhan_data`` 的持久化对象
'''
from wuhan_data.database import Base, DBBase, DBSession
from sqlalchemy import Column, Integer, DateTime
import logging


logger = logging.getLogger(__name__)


class CrawlerWuhanData(Base, DBBase):
    '''
        表 ``crawlerwuhandata`` 的持久化对象
    '''
    __tablename__ = 'crawlerwuhandata'

    instance_id = Column('instance_id', Integer, primary_key=True)
    start_time = Column('start_time', DateTime)
    finish_time = Column('finish_time', DateTime)
    item_scraped_count = Column('item_scraped_count', Integer)
    file_count = Column('file_count', Integer)
    file_status_count_uptodate = Column('file_status_count/uptodate', Integer)
    drop_item_count = Column('drop_item_count', Integer)
    failed_file_count = Column('failed_file_count', Integer)

    @classmethod
    def insert(cls, obj):
        '''
            插入对象
        '''
        with DBSession() as session:
            session.add(obj)
            session.flush()
