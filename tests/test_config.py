# -*- coding: utf-8 -*-
#
# Author: QianfuFinance
#
'''
    Test ``wuhan_data.config``
'''
from wuhan_data.config import ObjectNotDictError, DictAsClass, Config
from nose.tools import assert_equals


def test_objectnotdicterror():
    '''
        UnitTest ``wuhan_data.config.ObjectNotDictError``
    '''
    assert_equals(
        'Try to inialize with a non-dict object: test',
        str(ObjectNotDictError('test'))
    )


def test_dictasclass():
    '''
        UnitTest ``wuhan_data.config.DictAsClass``
    '''
    example = {
        'test': 'test',
        'test_dict': {
            'test': 'test'
        }
    }
    test_ins = DictAsClass(example)
    assert_equals(
        test_ins.test,
        'test'
    )
    assert_equals(
        test_ins.test_dict.test,
        'test'
    )


def test_Config():
    '''
        UnitTest ``wuhan_data.config.Config``
    '''
    config = Config('test_config.yml')
    assert_equals(
        config.test,
        'test'
    )
    assert_equals(
        config.test_dict.test,
        'test'
    )
