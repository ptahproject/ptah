""" event model """
import ptah
import pyramid_sqla
import sqlalchemy as sqla

Base = pyramid_sqla.get_base()
Session = pyramid_sqla.get_session()


class PtahEvent(Base):

    __tablename__ = 'ptah_events'

    id = sqla.Column(sqla.Integer, primary_key=True)
    uri = sqla.Column(sqla.Unicode)
    time = sqla.Column(sqla.DateTime)
    context = sqla.Column(sqla.Unicode)
    principal = sqla.Column(sqla.Unicode)
    path = sqla.Column(sqla.Unicode)
    data = sqla.Column(ptah.JsonDictType(), default={})
