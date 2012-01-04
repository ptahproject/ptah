import json
from threading import local

import sqlalchemy as sqla
from sqlalchemy import orm
from sqlalchemy.ext import declarative
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, TEXT
from zope.sqlalchemy import ZopeTransactionExtension

_base = declarative.declarative_base()
_zte = ZopeTransactionExtension()
_session = orm.scoped_session(orm.sessionmaker(extension=[_zte]))


def get_base():
    """Return the central SQLAlchemy declarative base."""
    return _base


def reset_session():
    """Reset sqla session"""
    global _zte, _session

    _zte = ZopeTransactionExtension()
    _session = orm.scoped_session(orm.sessionmaker(extension=[_zte]))


def get_session():
    """Return the central SQLAlchemy contextual session.

    To customize the kinds of sessions this contextual session creates, call
    its ``configure`` method::

        ptah.get_session().configure(...)

    But if you do this, be careful about the 'ext' arg. If you pass it, the
    ZopeTransactionExtension will be disabled and you won't be able to use this
    contextual session with transaction managers. To keep the extension active
    you'll have to re-add it as an argument. The extension is accessible under
    the semi-private variable ``_zte``. Here's an example of adding your own
    extensions without disabling the ZTE::

        ptah.get_session().configure(ext=[ptah._zte, ...])
    """
    return _session


class QueryFreezer(object):
    """ A facade for sqla.Session.query which caches internal query structure.

    :param builder: anonymous function containing SQLAlchemy query

    .. code-block:: python

        _sql_parent = ptah.QueryFreezer(
            lambda: Session.query(Content)
                .filter(Content.__uri__ == sqla.sql.bindparam('parent')))
    """
    _testing = False

    def __init__(self, builder):
        self.builder = builder
        self.data = local()

    def reset(self):
        self.data = local()

    def iter(self, **params):
        data = self.data
        if not hasattr(data, 'query') or self._testing:
            data.query = self.builder()
            data.mapper = data.query._mapper_zero_or_none()
            data.querycontext = data.query._compile_context()
            data.querycontext.statement.use_labels = True
            data.stmt = data.querycontext.statement

        conn = data.query._connection_from_session(
            mapper=data.mapper,
            clause=data.stmt,
            close_with_result=True)

        result = conn.execute(data.stmt, **params)
        return data.query.instances(result, data.querycontext)

    def one(self, **params):
        ret = list(self.iter(**params))

        l = len(ret)
        if l == 1:
            return ret[0]
        elif l == 0:
            raise orm.exc.NoResultFound("No row was found for one()")
        else:
            raise orm.exc.MultipleResultsFound(
                "Multiple rows were found for one()")

    def first(self, **params):
        ret = list(self.iter(**params))[0:1]
        if len(ret) > 0:
            return ret[0]
        else:
            return None

    def all(self, **params):
        return list(self.iter(**params))


class JsonType(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MutationList(Mutable, list):

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationList):
            if isinstance(value, list):
                return MutationList(value)
            return Mutable.coerce(key, value)  # pragma: no cover
        else:
            return value

    def append(self, value):
        list.append(self, value)
        self.changed()

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()


class MutationDict(Mutable, dict):

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationDict):
            if isinstance(value, dict):
                return MutationDict(value)
            return Mutable.coerce(key, value)  # pragma: no cover
        else:
            return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()


def JsonDictType():
    """
    function which returns a SQLA Column Type suitable to store a Json dict.

    :returns: ptah.sqla.MutationDict
    """
    return MutationDict.as_mutable(JsonType)


def JsonListType():
    """
    function which returns a SQLA Column Type suitable to store a Json array.

    :returns: ptah.sqla.MutationList
    """

    return MutationList.as_mutable(JsonType)
