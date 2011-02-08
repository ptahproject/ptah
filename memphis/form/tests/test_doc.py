##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""memphis.form Test Module"""
import re, sys, doctest, unittest
from zope.testing import renormalizing

import pyramid.testing

import memphis.config
from memphis.config import testing
from memphis.form.tests import outputchecker


def setUp(test):
    memphis.config.loadPackage('memphis.form')
    pyramid.testing.setUp()
    testing.setUpConfig(test)
    testing.setUpTestAsModule(test, 'memphis.TESTS')


def tearDown(test):
    pyramid.testing.tearDown()
    testing.tearDownConfig(test)
    testing.tearDownTestAsModule(test)


def test_suite():
    checker = outputchecker.OutputChecker(doctest)

    return unittest.TestSuite((
            doctest.DocFileSuite(
                '../widget.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../form.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            #doctest.DocFileSuite(
            #    '../group.txt',
            #    setUp=setUp, tearDown=tearDown,
            #    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            #    checker=checker,
            #    ),
            doctest.DocFileSuite(
                '../subform.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../button.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../action.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../datamanager.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../field.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../converter.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=renormalizing.RENormalizing([
                        (re.compile(
                                r"(invalid literal for int\(\)) with base 10: '(.*)'"),
                        r'\1: \2'),
                        (re.compile(
                                r"Decimal\('(.*)'\)"),
                         r'Decimal("\1")'),
                        ])
                ),
            doctest.DocFileSuite(
                '../error.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../util.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            doctest.DocFileSuite(
                '../term.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                ),
            ))
