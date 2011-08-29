""" models """
import datetime
import uuid, transaction
import pyramid_sqla as psa
import sqlalchemy as sa
import sqlalchemy.orm as orm
from memphis import config

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


@config.handler(config.SettingsInitialized)
def initialize(ev):
    # Create all tables
    Base.metadata.create_all()

    # Commit changes
    transaction.commit()
