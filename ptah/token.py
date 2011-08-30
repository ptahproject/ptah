""" simple token service """
import datetime
import uuid, transaction
import pyramid_sqla as psa
import sqlalchemy as sa
import sqlalchemy.orm as orm
from memphis import config
from zope import interface
from zope.component import getSiteManager

__all__ = ['registerTokenType', 'tokenService', 'ITokenType', 'ITokenService']


class ITokenType(interface.Interface):
    """ Token type interface

    ``id`` unique token type id. Token service uses this id
    for token type identification in tokens storage.

    ``timeout`` token timout, it has to be timedelta instance.
    """

    id = interface.Attribute('Unique type id')

    timeout = interface.Attribute('Token timeout')


class ITokenService(interface.Interface):
    """ Token management service """

    def generate(type, data):
        """ Generate and return string token.

        ``type`` object implemented ITokenType interface.

        ``data`` token type specific data, it must be python string. """

    def get(token, type, data=None):
        """ Get data for token """

    def getToken(type, data):
        """ Get token for data """

    def remove(token):
        """ Remove token """


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

    def getToken(self, typ, data):
        t = Token.getToken(data, typ.id)
        if t is not None:
            return t.token

    def remove(self, token):
        Session.query(Token).filter(Token.token == token).delete()


tokenService = TokenService()


Base = psa.get_base()
Session = psa.get_session()


class Token(Base):

    __tablename__ = 'ptah_tokens'

    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.Unicode(48))
    time = sa.Column(sa.DateTime)
    token = sa.Column(sa.Unicode(48))
    data = sa.Column(sa.Unicode)

    def __init__(self, type, data):
        super(Token, self).__init__()

        self.type = type
        self.data = data
        self.time = datetime.datetime.now()
        self.token = str(uuid.uuid4())

    @classmethod
    def get(cls, token, type):
        return Session.query(cls).filter_by(token=token, type=type).first()

    @classmethod
    def getToken(cls, data, type):
        return Session.query(cls).filter_by(data=data, type=type).first()


@config.handler(config.SettingsInitialized)
def initialize(ev):
    # Create all tables
    Base.metadata.create_all()

    # Commit changes
    transaction.commit()
