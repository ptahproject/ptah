""" tests """
import unittest, doctest, sys
from zope import interface, component

from pyramid.exceptions import NotFound
from pyramid.interfaces import IView, IViewClassifier

import memphis
from memphis import config
from memphis.config import testing


class Content(object):

    def __init__(self, iface=interface.Interface, **kw):
        interface.directlyProvides(self, iface)

        self.__dict__.update(kw)


def getPyramidView(request, context, name, call=False):
    sm = component.getSiteManager()

    factory = sm.adapters.lookup(
        (IViewClassifier,
         interface.providedBy(request),
         interface.providedBy(context)), IView, name=name)

    if call:
        return factory(context, request)
    else:
        return factory.view(context, request)


def setUp(test):
    config.loadPackage('memphis.view')

    test.globs['Content'] = Content
    test.globs['getPyramidView'] = getPyramidView

    testing.setUpConfig(test)
    testing.setUpTestAsModule(test, 'memphis.TESTS')
    memphis.TESTS = sys.modules['memphis.TESTS']


def tearDown(test):
    testing.tearDownTestAsModule(test)
    testing.tearDownConfig(test)
    del memphis.TESTS


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'pagelet.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'view.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'message.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
