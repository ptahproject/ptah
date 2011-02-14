""" memphis.view interfaces

$Id: interfaces.py 11635 2011-01-18 07:03:08Z fafhrd91 $
"""
from zope import interface
from pyramid.interfaces import IView


class LayoutNotFound(LookupError):
    """ Layout not found exception """


class IPagelet(interface.Interface):
    """ pagelet """

    context = interface.Attribute('Context')

    contexts = interface.Attribute('Additional contexts')

    layoutname = interface.Attribute('Layout name')

    isRedirected = interface.Attribute('is redirected')

    def redirect(url=''):
        """Redirect URL, if `update` method needs redirect,
        it should call `redirect` method, __call__ method should
        check isRendered before render or layout."""

    def update():
        """Update the pagelet data."""

    def render():
        """Render the pagelet content w/o o-wrap."""

    def updateAndRender():
        """Update pagelet and render. Prefered way to render pagelet."""

    def isAvailable():
        """Is available"""


class IPageletType(interface.Interface):
    """ pagelet interface type """


class ILayout(interface.Interface):
    """ layout """

    template = interface.Attribute('Layout template')

    view = interface.Attribute('Parent view')
    context = interface.Attribute('Parent view context')

    mainview = interface.Attribute('Initial view')
    maincontext = interface.Attribute('Initial view context')

    template = interface.Attribute('Layout template')

    def update():
        """Update the layout data """

    def render():
        """Render the layout """

    def __call__(layout=None, view=None, *args, **kw):
        """ build layout tree and render """


class IDefaultView(interface.Interface):
    """ default view """

    name = interface.Attribute("Name of default view")


# navigation root
class INavigationRoot(interface.Interface):
    """ site root """


# status message
class IMessage(interface.Interface):
    """ message """

    def render(message):
        """ render message """


class IStatusMessage(interface.Interface):
    """ message service """

    def add(text, type='info'):
        """ add message text as message to service """

    def clear():
        """ return all mesasges and clear """

    def messages():
        """ return all messages """


# view action
class IAction(interface.Interface):
    """ view action """

    name = interface.Attribute('Name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    def url(request):
        """ build url for action """
