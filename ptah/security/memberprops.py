""" member properties """
import sqlalchemy as sqla
import pyramid_sqla as psqla
from datetime import datetime

from ptah.query import QueryFreezer
from ptah.utils import JsonDictType
from ptah.security import IPrincipal

Base = psqla.get_base()
Session = psqla.get_session()


class MemberProperties(Base):

    __tablename__ = 'ptah_memberprops'

    uuid = sqla.Column(sqla.Unicode, primary_key=True)
    joined = sqla.Column(sqla.DateTime)
    validated = sqla.Column(sqla.Boolean, default=False)
    suspended = sqla.Column(sqla.Boolean, default=False)
    keywords = sqla.Column('keywords', JsonDictType(), default={})

    def __init__(self, uuid):
        super(Base, self).__init__()

        self.uuid = uuid
        self.joined = datetime.now()
        self.validated = False
        self.suspended = False

    _sql_get = QueryFreezer(
        lambda: Session.query(MemberProperties)
        .filter(MemberProperties.uuid == sqla.sql.bindparam('uuid')))

    @classmethod
    def get(cls, id):
        props = cls._sql_get.first(uuid=id)
        if props is None:
            props = MemberProperties(id)
            Session.add(props)
            Session.flush()
        return props
