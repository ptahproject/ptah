""" token service implementation """
from zope import interface
from zope.component import getSiteManager

from memphis import config

from models import Session, Token
from interfaces import ITokenType, ITokenService


types = {}

class TokenType(object):
    interface.implements(ITokenType)

    def __init__(self, id, timeout, title, description):
        self.id = id
        self.timeout = timeout
        self.title = title
        self.description = description


def registerTokenType(id, timeout, title='', description=''):
    tt = TokenType(id, timeout, title, description)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            registerTokenTypeImpl,
            (tt, ), discriminator = ('ptah.token:tokenType', id)))

    return tt


def registerTokenTypeImpl(tt):
    types[tt.id] = tt


def tokenService():
    return getSiteManager().getUtility(ITokenService)


class TokenService(object):
    interface.implements(ITokenService)
    config.utility(ITokenService)

    def generate(self, typ, data):
        t = Token(typ.id, data)
        Session.add(t)

        return t.token

    def get(self, typ, token, data=None):
        t = Token.get(token, typ.id)
        if t is not None:
            return t.data

    def remove(self, token):
        Session.query(Token).filter(Token.token == token).delete()
