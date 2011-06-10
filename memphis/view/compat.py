""" pyramid/zope compatibility """
from zope import interface
try:
    from zope.publisher.interfaces.browser \
        import IBrowserView as IZopeView
    from zope.publisher.interfaces.browser \
        import IBrowserRequest as IZopeRequest
except ImportError:
    class IZopeView(interface.Interface):
        pass
    class IZopeRequest(interface.Interface):
        pass

try:
    from pyramid.interfaces import IView as IPyramidView
    from pyramid.interfaces import IRequest as IPyramidLayer
except:
    class IPyramidView(interface.Interface):
        pass
    class IPyramidLayer(interface.Interface):
        pass


from interfaces import IView


class IView(IView, IZopeView, IPyramidView):
    """ view """


class IRequest(IZopeRequest, IPyramidLayer):
    """ view """
