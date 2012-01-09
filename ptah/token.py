""" simple token service """
import uuid
import datetime
import sqlalchemy as sqla

import ptah
from ptah import config
from ptah.sqlautils import QueryFreezer

__all__ = ['TokenType', 'service']

ID_TOKEN_TYPE = 'ptah:token-type'


class TokenType(object):
    """ Token type interface

    ``id`` unique token type id. Token service uses this id
    for token type identification in tokens storage.

    ``timeout`` token timout, it has to be timedelta instance.
    """

    def __init__(self, id, timeout, title='', description=''):
        self.id = id
        self.timeout = timeout
        self.title = title
        self.description = description

        info = config.DirectiveInfo()
        discr = (ID_TOKEN_TYPE, id)
        intr = config.Introspectable(ID_TOKEN_TYPE, discr, title, ID_TOKEN_TYPE)
        intr['ttype'] = self
        intr['codeinfo'] = info.codeinfo

        info.attach(
            config.Action(
                lambda config, id, tp: \
                    config.get_cfg_storage(ID_TOKEN_TYPE).update({id: tp}),
                (id, self), discriminator=discr, introspectables=(intr,))
            )


class TokenService(object):
    """ Token management service """

    _sql_get = QueryFreezer(
        lambda: ptah.get_session().query(Token).filter(
            Token.token == sqla.sql.bindparam('token')))

    _sql_get_by_data = QueryFreezer(
        lambda: ptah.get_session().query(Token).filter(
            sqla.sql.and_(Token.data == sqla.sql.bindparam('data'),
                          Token.typ == sqla.sql.bindparam('typ'))))

    def generate(self, typ, data):
        """ Generate and return string token.

        ``type`` object implemented ITokenType interface.

        ``data`` token type specific data, it must be python string. """

        t = Token(typ, data)

        Session = ptah.get_session()
        Session.add(t)
        Session.flush()
        return t.token

    def get(self, token):
        """ Get data for token """
        t = self._sql_get.first(token=token)
        if t is not None:
            return t.data

    def get_bydata(self, typ, data):
        """ Get token for data """
        t = self._sql_get_by_data.first(data=data, typ=typ.id)
        if t is not None:
            return t.token

    def remove(self, token):
        """ Remove token """
        ptah.get_session().query(Token).filter(
            sqla.sql.or_(Token.token == token,
                         Token.valid > datetime.datetime.now())).delete()


service = TokenService()

class Token(ptah.get_base()):

    __tablename__ = 'ptah_tokens'

    id = sqla.Column(sqla.Integer, primary_key=True)
    token = sqla.Column(sqla.Unicode(48))
    valid = sqla.Column(sqla.DateTime)
    data = sqla.Column(sqla.Text)
    typ = sqla.Column('type', sqla.Unicode(48))

    def __init__(self, typ, data):
        super(Token, self).__init__()

        self.typ = typ.id
        self.data = data
        self.valid = datetime.datetime.now() + typ.timeout
        self.token = uuid.uuid4().hex
