# This file is necessary to make this directory a package.

from memphis.view.pagelet import Pagelet
from memphis.view.pagelet import renderPagelet
from memphis.view.pagelet import registerPagelet
from memphis.view.layout import Layout
from memphis.view.layout import registerLayout
from memphis.view.view import View
from memphis.view.view import renderView
from memphis.view.view import registerView
from memphis.view.view import registerDefaultView
from memphis.view.path import template
from memphis.view.message import addStatusMessage

# directives
from memphis.view.directives import pyramidView
from memphis.view.directives import pageletType

from memphis.view.interfaces import IRoot


import zope.interface
class Root(object):
    zope.interface.implements(IRoot)

    __name__ = ''
    __parent__ = None

Root = Root()
