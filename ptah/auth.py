""" """
from zope import interface
from zope.component import getUtility

from pyramid import security
from pyramid.threadlocal import get_current_request

from memphis import config
from ptah.interfaces import IAuthentication
from ptah.crowd.models import User
from ptah.crowd.interfaces import IPasswordTool


class Principal(object):

    def __init__(self, id, name, login, suspended):
        self.id = id
        self.name = name
        self.login = login
        self.suspended = suspended


class Authentication(object):
    config.utility(IAuthentication)

    def authenticate(self, login, password):
        user = User.get(login)

        if user is not None:
            pwtool = getUtility(IPasswordTool)
            if pwtool.checkPassword(user.password, password):
                return Principal(user.id, user.name,
                                 user.login, user.suspended)

    def getUser(self, id):
        if id and id.startswith('memphis-'):
            try:
                user = storage.getItem(id[8:])
                user.id = id
                return user
            except:
                pass

    def getUserByLogin(self, login):
        user = User.get(login)
        if user is not None:
            return Principal(user.id, user.name, user.login, user.suspended)

    def getCurrentUser(self):
        id = security.authenticated_userid(get_current_request())
        if id:
            return self.getUserByLogin(id)

    def getCurrentLogin(self, request=None):
        if request is None:
            request = get_current_request()
        return security.authenticated_userid(request)
