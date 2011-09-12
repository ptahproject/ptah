""" models """
import datetime
import pyramid_sqla as psa
import sqlalchemy as sa
import sqlalchemy.orm as orm
from memphis import config
from zope import interface

import ptah
from ptah.security import IPrincipalWithEmail

Base = psa.get_base()
Session = psa.get_session()
UUID = ptah.UUIDGenerator('user+crowd')


class CrowdUser(Base):
    interface.implements(IPrincipalWithEmail)

    __tablename__ = 'ptah_crowd'

    pid = sa.Column(sa.Integer, primary_key=True)
    uuid = sa.Column(sa.Unicode(45), unique=True)
    name = sa.Column(sa.Unicode(255))
    login = sa.Column(sa.Unicode(255), unique=True)
    email = sa.Column(sa.Unicode(255), unique=True)
    password = sa.Column(sa.Unicode(255))

    def __init__(self, name, login, email, password=u''):
        super(Base, self).__init__()

        self.name = name
        self.uuid = UUID()
        self.login = login
        self.email = email
        self.password = password

    @classmethod
    def get(cls, id):
        return Session.query(cls).filter(cls.uuid==id).first()

    @classmethod
    def getById(cls, id):
        return Session.query(cls).filter(cls.id==id).first()

    @classmethod
    def getByLogin(cls, login):
        return Session.query(cls).filter(cls.login==login).first()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s <%s>'%(self.name, self.uuid)


@config.handler(config.SettingsInitialized)
def initialize(ev):
    # Create all tables
    Base.metadata.create_all()
