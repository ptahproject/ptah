""" ptah route """
from zope import interface
from memphis import view


class PtahRoute(object):
    interface.implements(view.INavigationRoot)

    __name__ = None
    __parent__ = None


ptahRoute = PtahRoute()


view.registerLayout(
    'ptah', PtahRoute, parent='.',
    template = view.template('ptah.views:login-layout.pt'))

