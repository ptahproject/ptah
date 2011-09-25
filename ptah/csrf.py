""" csrf service for memphis.form """
from datetime import timedelta
from ptah import token
from zope import interface
from memphis import config
from memphis.form.interfaces import ICSRFService


TOKEN_TYPE = token.TokenType(
    '1c49d2aacf844557a7aff3dbf09c0740', timedelta(minutes=30))


class CSRFService(object):
    interface.implements(ICSRFService)
    config.utility()

    def generate(self, data):
        t = token.service.getByData(TOKEN_TYPE, data)
        if t is not None:
            return t
        return token.service.generate(TOKEN_TYPE, data)

    def get(self, t):
        return token.service.get(t)

    def remove(self, t):
        return token.service.remove(t)
