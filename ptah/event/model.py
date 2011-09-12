""" event model """
import pyramid_sqla
import sqlalchemy as sqla
from ptah.utils import JsonDictType

Base = pyramid_sqla.get_base()
Session = pyramid_sqla.get_session()


class PtahEvent(Base):

    __tablename__ = 'ptah_events'

    id = sqla.Column(sqla.Integer, primary_key=True)
    uuid = sqla.Column(sqla.Unicode)
    time = sqla.Column(sqla.DateTime)
    context = sqla.Column(sqla.Unicode)
    principal = sqla.Column(sqla.Unicode)
    path = sqla.Column(sqla.Unicode)
    data = sqla.Column(JsonDictType(), default={})
