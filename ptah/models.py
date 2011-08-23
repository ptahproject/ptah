""" models """
import datetime
import uuid, transaction
import pyramid_sqla as psa
import sqlalchemy as sa
import sqlalchemy.orm as orm

from memphis import config

from ptah.crowd.models import User


Base = psa.get_base()
Session = psa.get_session()


class AuthToken(Base):

    __tablename__ = 'ptah_authtokens'

    id = sa.Column(
        sa.Integer, sa.Sequence('ptah_authtokens_seq'), primary_key=True)
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
    def get(cls, token, type):
        return Session.query(AuthToken) \
            .filter_by(token=token, type=type).first()


@config.handler(config.SettingsInitialized)
def initialize(ev):
    # Create all tables
    Base.metadata.create_all()

    # Commit changes
    transaction.commit()
