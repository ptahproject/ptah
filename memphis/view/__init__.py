# This file is necessary to make this directory a package.

from memphis.view.path import template

from memphis.view.pagelet import Pagelet
from memphis.view.pagelet import renderPagelet
from memphis.view.pagelet import registerPagelet
from memphis.view.pagelet import registerPageletType

from memphis.view.layout import Layout
from memphis.view.layout import registerLayout

from memphis.view.view import View
from memphis.view.view import renderView
from memphis.view.view import registerView
from memphis.view.view import registerDefaultView

from memphis.view.message import addMessage

# directives
from memphis.view.directives import pagelet
from memphis.view.directives import pageletType
from memphis.view.directives import pyramidView


# view action
from memphis.view.action import Action
from memphis.view.interfaces import IAction


# root
from memphis.view.interfaces import INavigationRoot


import zope.interface
class Root(object):
    zope.interface.implements(INavigationRoot)

    __name__ = ''
    __parent__ = None

Root = Root()
