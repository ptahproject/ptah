# memphis.view public API

from memphis.view.path import path, template

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

# navigation root
import zope.interface
from memphis.view.interfaces import INavigationRoot


class Root(object):
    zope.interface.implements(INavigationRoot)

    __name__ = ''
    __parent__ = None

Root = Root()
