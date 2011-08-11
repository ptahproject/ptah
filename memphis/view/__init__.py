# memphis.view public API

# interfaces
from memphis.view.interfaces import IRenderer
from memphis.view.interfaces import ISimpleView
from memphis.view.interfaces import IView

# path/template
from memphis.view.path import path
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
from memphis.view.view import SimpleView
from memphis.view.view import subpath
from memphis.view.view import json

# pyramid view
try:
    from memphis.view.compat_pyramid import renderView
    from memphis.view.compat_pyramid import registerView
    from memphis.view.compat_pyramid import registerDefaultView
except ImportError:
    import sys, types
    compat_pyramid = types.ModuleType('memphis.view.compat_pyramid')
    sys.modules['memphis.view.compat_pyramid'] = compat_pyramid

# zope view
try:
    from memphis.view.compat_zope import ZopeLayout
    from memphis.view.compat_zope import registerZopeView
    from memphis.view.compat_zope import registerZopeDefaultView
except ImportError:
    import sys, types
    compat_zope = types.ModuleType('memphis.view.compat_zope')
    sys.modules['memphis.view.compat_zope'] = compat_zope

# directives
from memphis.view.directives import layout
from memphis.view.directives import pagelet
from memphis.view.directives import pageletType
from memphis.view.directives import zopeView
from memphis.view.directives import pyramidView

# status message
from memphis.view.message import addMessage

# format
from memphis.view.formatter import format

# compat api
from memphis.view.compat import getLocale
from memphis.view.compat import translate
from memphis.view.compat import TranslationStringFactory

# navigation root
import zope.interface
from memphis.view.interfaces import INavigationRoot


class Root(object):
    zope.interface.implements(INavigationRoot)

    __name__ = ''
    __parent__ = None

Root = Root()
