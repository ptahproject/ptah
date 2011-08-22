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

    __tablename__ = 'memphis_users'

    id = sa.Column(sa.Integer, 
                   sa.Sequence('memphis_users_seq'), primary_key=True)
    login = sa.Column(sa.Unicode(255), unique=True)
    email = sa.Column(sa.Unicode(255), unique=True)
    password = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode(255))
    joined = sa.Column(sa.DateTime)
    validated = sa.Column(sa.Boolean)

    def __init__(self, login, email, password):
        super(Base, self).__init__()

        self.login = login
        self.email = email
        self.password = password
        self.joined = datetime.datetime.now()
        self.validated = False

        self.token = str(uuid.uuid4())

    @classmethod
    def get(self, login):
        return Session.query(User).filter_by(login=login).first()

    @classmethod
    def getById(self, id):
        return Session.query(User).filter_by(id=id).first()


class AuthToken(Base):

    __tablename__ = 'memphis_authtokens'

    id = sa.Column(sa.Integer, 
                   sa.Sequence('memphis_authtokens_seq'), primary_key=True)
    type = sa.Column(sa.Integer)
    time = sa.Column(sa.DateTime)
    token = sa.Column(sa.Unicode(48))
    data = sa.Column(sa.Unicode)

    def __init__(self, type, data):
        super(AuthToken, self).__init__()

        self.type = type
        self.data = data
        self.time = datetime.datetime.now()
        self.token = str(uuid.uuid4())

    @classmethod
    def get(self, token, type):
        return Session.query(AuthToken).filter_by(
            token=token, type=type).first()


@config.handler(config.SettingsInitialized)
def initialize(ev):
    # Create all tables
    Base.metadata.create_all()

    # Commit changes
    transaction.commit()
