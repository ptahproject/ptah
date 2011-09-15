""" simple token service """
import datetime, uuid
import pyramid_sqla as psa
import sqlalchemy as sqla
from zope import interface
from memphis import config
from ptah.query import QueryFreezer

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

    def get(token):
        """ Get data for token """

    def getByData(type, data):
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
    types[tt.id] = tt

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            None, discriminator = ('ptah.token:tokenType', id)))

    return tt


class TokenService(object):
    interface.implements(ITokenService)

    _sql_get = QueryFreezer(
        lambda: Session.query(Token).filter(
            Token.token==sqla.sql.bindparam('token')))

    _sql_get_by_data = QueryFreezer(
        lambda: Session.query(Token).filter(
            sqla.sql.and_(Token.data==sqla.sql.bindparam('data'),
                          Token.typ==sqla.sql.bindparam('typ'))))

    def generate(self, typ, data):
        t = Token(typ, data)
        Session.add(t)
        return t.token

    def get(self, token):
        t = self._sql_get.first(token=token)
        if t is not None:
            return t.data

    def getByData(self, typ, data):
        t = self._sql_get_by_data.first(data=data, typ=typ.id)
        if t is not None:
            return t.token

    def remove(self, token):
        Session.query(Token).filter(
            sqla.sql.or_(Token.token == token,
                         Token.valid > datetime.datetime.now())).delete()


tokenService = TokenService()

Base = psa.get_base()
Session = psa.get_session()


class Token(Base):

    __tablename__ = 'ptah_tokens'

    id = sqla.Column(sqla.Integer, primary_key=True)
    token = sqla.Column(sqla.Unicode(48))
    valid = sqla.Column(sqla.DateTime)
    data = sqla.Column(sqla.Unicode)
    typ = sqla.Column(sqla.Unicode(48))

    def __init__(self, typ, data):
        super(Token, self).__init__()

        self.typ = typ.id
        self.data = data
        self.valid = datetime.datetime.now() + typ.timeout
        self.token = str(uuid.uuid4())
