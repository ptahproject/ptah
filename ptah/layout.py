""" ptah route """
from zope import interface
from memphis import view
from ptah.interfaces import IPtahRoute


class PtahRoute(object):
    interface.implements(IPtahRoute)

    __name__ = '/ptah/'
    __parent__ = view.DefaultRoot()


ptahRoute = PtahRoute()


view.registerRoute(
    'ptah', '/ptah/*traverse', lambda request: ptahRoute)


view.registerLayout(
    '', IPtahRoute, parent='.',
    template = view.template('ptah.views:ptah-layout.pt'))


view.registerLayout(
    'ptah-exception', parent='.',
    template = view.template('ptah.views:ptah-exception.pt'))
