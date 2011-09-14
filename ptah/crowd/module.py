""" introspect module """
import ptah
from zope import interface
from memphis import config, view
from interfaces import ICrowdModule, ICrowdUser

from models import CrowdUser as SQLUser


class CrowdModule(ptah.PtahModule):
    """ Basic user management module. """

    config.utility(name='crowd')
    interface.implementsOnly(ICrowdModule)

    name = 'crowd'
    title = 'Crowd'
    description = 'Basic user management module.'

    def __getitem__(self, key):
        if key:
            user = SQLUser.getById(key)
            if user is not None:
                return CrowdUser(user, self)

        raise KeyError(key)


class CrowdUser(object):
    interface.implements(ICrowdUser)

    def __init__(self, user, parent):
        self.user = user
        self.__name__ = str(user.pid)
        self.__parent__ = parent


view.registerPagelet(
    'ptah-module-actions', ICrowdModule,
    template = view.template('ptah.crowd:templates/actions.pt'))
