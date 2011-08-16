# memphis.view public API

# interfaces
from memphis.view.interfaces import IRenderer
from memphis.view.interfaces import ISimpleView
from memphis.view.interfaces import IView
from memphis.view.interfaces import ILayout
from memphis.view.interfaces import IPageletType

# path/template
from memphis.view.tmpl import path, template

# view utils
from memphis.view.base import BaseMixin

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
from memphis.view.view import SimpleView
from memphis.view.view import subpath
from memphis.view.view import json

# pyramid view
from memphis.view.compat_pyramid import renderView
from memphis.view.compat_pyramid import registerView
from memphis.view.compat_pyramid import registerDefaultView

# custom
from memphis.view.customize import custom

# resource
from memphis.view.resources import static
from memphis.view.resources import static_url

# resource library
from memphis.view.library import library
from memphis.view.library import include
from memphis.view.library import renderIncludes

# directives
from memphis.view.directives import layout
from memphis.view.directives import pagelet
from memphis.view.directives import pageletType
from memphis.view.directives import pyramidView

# status message
from memphis.view.message import addMessage
from memphis.view.message import renderMessages

# format
from memphis.view.formatter import format

# navigation root
import zope.interface
from memphis.view.interfaces import INavigationRoot


class Root(object):
    zope.interface.implements(INavigationRoot)

    __name__ = ''
    __parent__ = None

Root = Root()
