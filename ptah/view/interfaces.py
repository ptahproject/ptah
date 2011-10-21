""" ptah.view interfaces """
from zope import interface
from pyramid.interfaces import IView as IPyramidView


class IPtahView(IPyramidView):
    """ ptah view """

    __name__ = interface.Attribute('Name')
    __parent__ = interface.Attribute('Parent')

    context = interface.Attribute('Context')
    request = interface.Attribute('Request')

    def update():
        """Update the snippet data."""

    def __call__():
        """ render view """


class ISnippet(interface.Interface):
    """ snippet """

    context = interface.Attribute('Context')

    request = interface.Attribute('Request')

    template = interface.Attribute('Template')

    def update():
        """Update the snippet data."""

    def render():
        """Render the snippet."""

    def __call__():
        """Update and render snippet"""


class ILayout(interface.Interface):
    """ layout """

    template = interface.Attribute('Layout template')

    view = interface.Attribute('Initial view')
    viewcontext = interface.Attribute('Initial view context')

    template = interface.Attribute('Layout template')

    def update():
        """Update the layout data """

    def render(content, **kwargs):
        """Render the layout """

    def __call__(content, layout=None, view=None, *args, **kw):
        """ build layout tree and render """


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
