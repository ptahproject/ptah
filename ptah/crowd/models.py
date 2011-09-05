""" models """
import datetime
import uuid, transaction
import pyramid_sqla as psa
import sqlalchemy as sa
import sqlalchemy.orm as orm
from memphis import config

Base = psa.get_base()
Session = psa.get_session()


class User(Base):

    __tablename__ = 'ptah_crowd'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255))
    login = sa.Column(sa.Unicode(255), unique=True)
    email = sa.Column(sa.Unicode(255), unique=True)
    password = sa.Column(sa.Unicode(255))
    joined = sa.Column(sa.DateTime)
    validated = sa.Column(sa.Boolean)
    suspended = sa.Column(sa.Boolean)

    def __init__(self, name, login, email, password=u''):
        super(Base, self).__init__()

        self.name = name
        self.login = login
        self.email = email
        self.password = password
        self.joined = datetime.datetime.now()
        self.validated = False
        self.suspended = False

    @classmethod
    def get(cls, login):
        return Session.query(User).filter(cls.login==login).first()

    @classmethod
    def getById(cls, id):
        return Session.query(User).filter(cls.id==id).first()


class UserActivity(Base):

    __tablename__ = 'ptah_crowd_activity'

    id = sa.Column(sa.Integer, primary_key=True)
    user = sa.Column(sa.Integer)
    date = sa.Column(sa.DateTime)
    type = sa.Column(sa.Unicode(10))

    def __init__(self, user, type):
        super(UserActivity, self).__init__()

        self.user = user
        self.date = datetime.now()
        self.type = type


class UserProps(Base):

    __tablename__ = 'ptah_crowd_testprops'

    id = sa.Column(sa.Integer, primary_key=True)
    user = sa.Column(sa.Integer)
    date = sa.Column(sa.DateTime)
    title = sa.Column(sa.Unicode(10))

    def __init__(self, user):
        super(UserProps, self).__init__()
    
        self.user = user

    @classmethod
    def get(cls, id):
        return Session.query(cls).filter(cls.user==id).first()


@config.handler(config.SettingsInitialized)
def initialize(ev):
    # Create all tables
    Base.metadata.create_all()

    # Commit changes
    transaction.commit()
