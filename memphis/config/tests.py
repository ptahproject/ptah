""" memphis.config tests """
import sys, unittest, doctest
from testing import setUpConfig, tearDownConfig
from testing import setUpTestAsModule, tearDownTestAsModule

import memphis.config


def setUp(test):
    memphis.config.loadPackage('memphis.config')
    setUpConfig(test)
    setUpTestAsModule(test, 'memphis.config.TESTS')
    memphis.config.TESTS = sys.modules['memphis.config.TESTS']


def tearDown(test):
    tearDownConfig(test)
    tearDownTestAsModule(test)
    del memphis.config.TESTS


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                './README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.config.api',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'memphis.config.meta',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
