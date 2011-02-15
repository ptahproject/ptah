# memphis.view public API

from memphis.view.path import template

# pagelet
from memphis.view.pagelet import Pagelet
from memphis.view.pagelet import renderPagelet
from memphis.view.pagelet import registerPagelet
from memphis.view.pagelet import registerPageletType

# layout
from memphis.view.layout import Layout
from memphis.view.layout import registerLayout

# view
from memphis.view.view import View
from memphis.view.view import renderView
from memphis.view.view import registerView
from memphis.view.view import registerDefaultView

# directives
from memphis.view.directives import pagelet
from memphis.view.directives import pageletType
from memphis.view.directives import pyramidView

# status message
from memphis.view.message import addMessage

# view action
from memphis.view.interfaces import IAction
from memphis.view.action import Action, registerAction, registerActions

# navigation root
import zope.interface
from memphis.view.interfaces import INavigationRoot

class Root(object):
    zope.interface.implements(INavigationRoot)

    __name__ = ''
    __parent__ = None

Root = Root()
