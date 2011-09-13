""" csrf service for memphis.form """
from datetime import timedelta
from ptah import token
from zope import interface
from memphis import config
from memphis.form.interfaces import ICSRFService


TOKEN_TYPE = token.registerTokenType(
    'cc2a8158-ea1e-4f04-b94c-5346fca9d7c3', timedelta(minutes=30))


class CSRFService(object):
    interface.implements(ICSRFService)
    config.utility()

    def generate(self, data):
        t = token.tokenService.getByData(TOKEN_TYPE, data)
        if t is not None:
            return t
        return token.tokenService.generate(TOKEN_TYPE, data)

    def get(self, t):
        return token.tokenService.get(t)

    def remove(self, t):
        return token.tokenService.remove(t)
