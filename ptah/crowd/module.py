""" introspect module """
import ptah
from memphis import config
from zope import interface

from interfaces import ICrowdModule, ICrowdUser


class CrowdModule(ptah.PtahModule):
    config.utility(name='crowd')
    interface.implementsOnly(ICrowdModule)

    name = 'crowd'
    title = 'Crowd'
    description = 'Basic user management module.'


class User(object):
    interface.implements(ICrowdUser)

    def __init__(self, user, parent):
        self.user = user
        self.__name__ = str(user.id)
        self.__parent__ = parent
