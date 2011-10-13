""" member properties """
import ptah
import sqlalchemy as sqla
import pyramid_sqla as psqla
from datetime import datetime

Base = psqla.get_base()
Session = psqla.get_session()


class MemberProperties(Base):

    __tablename__ = 'ptah_memberprops'

    uri = sqla.Column(sqla.Unicode, primary_key=True)
    joined = sqla.Column(sqla.DateTime())
    validated = sqla.Column(sqla.Boolean(), default=False)
    suspended = sqla.Column(sqla.Boolean(), default=False)
    keywords = sqla.Column('keywords', ptah.JsonDictType(), default={})

    def __init__(self, uri):
        super(Base, self).__init__()

        self.uri = uri
        self.joined = datetime.now()
        self.validated = False
        self.suspended = False

    _sql_get = ptah.QueryFreezer(
        lambda: Session.query(MemberProperties)
        .filter(MemberProperties.uri == sqla.sql.bindparam('uri')))

    @classmethod
    def get(cls, id):
        props = cls._sql_get.first(uri=id)
        if props is None:
            props = MemberProperties(id)
            Session.add(props)
            Session.flush()
        return props
