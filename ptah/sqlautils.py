# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
    unicode_literals)  # Avoid breaking Python 3

import uuid
from threading import local

import sqlalchemy as sqla
from sqlalchemy import orm
from sqlalchemy.ext import declarative
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, TEXT
from zope.sqlalchemy import ZopeTransactionExtension

from ptah.util import json

_base = declarative.declarative_base()
_zte = ZopeTransactionExtension()
_session = orm.scoped_session(orm.sessionmaker(extension=[_zte]))
_session_maker = orm.sessionmaker()
_sa_session = local()


def get_base():
    """Return the central SQLAlchemy declarative base."""
    return _base


def reset_session():
    """Reset sqla session"""
    global _zte, _session

    _zte = ZopeTransactionExtension()
    _session = orm.scoped_session(orm.sessionmaker(extension=[_zte]))


class transaction(object):

    def __init__(self, sa):
        self.sa = sa

    def __enter__(self):
        global _sa_session

        t = getattr(_sa_session, 'transaction', None)
        if t is not None:
            raise RuntimeError("Nested transactions are not allowed")

        _sa_session.sa = self.sa
        _sa_session.transaction = self

        return self.sa

    def __exit__(self, type, value, traceback):
        global _sa_session
        _sa_session.sa = None
        _sa_session.transaction = None

        if type is None:
            try:
                self.sa.commit()
            except:
                self.sa.rollback()
                raise
        else:
            self.sa.rollback()


def sa_session():
    return transaction(_session_maker())


def get_session_maker():
    return _session_maker


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
    return getattr(_sa_session, 'sa', _session) or _session


class QueryFreezer(object):
    """ A facade for sqla.Session.query which caches internal query structure.

    :param builder: anonymous function containing SQLAlchemy query

    .. code-block:: python

        _sql_parent = ptah.QueryFreezer(
            lambda: Session.query(Content)
                .filter(Content.__uri__ == sqla.sql.bindparam('parent')))
    """

    def __init__(self, builder):
        self.id = uuid.uuid4().int
        self.builder = builder

    def reset(self):
        pass

    def iter(self, **params):
        sa = get_session()
        try:
            data = sa.__ptah_cache__
        except AttributeError:
            sa.__ptah_cache__ = data = {}

        q = data.get(self.id, None)

        if q is None:
            query = self.builder()
            mapper = query._mapper_zero_or_none()
            querycontext = query._compile_context()
            querycontext.statement.use_labels = True
            stmt = querycontext.statement
            data[self.id] = (query, mapper, querycontext, stmt)
        else:
            query, mapper, querycontext, stmt = q

        conn = query._connection_from_session(
            mapper=mapper,
            clause=stmt,
            close_with_result=True)

        result = conn.execute(stmt, **params)
        return query.instances(result, querycontext)

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


def set_jsontype_serializer(serializer):
    JsonType.serializer = serializer


class JsonType(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = TEXT
    serializer = json

    def __init__(self, serializer=None, *args, **kw):
        if serializer is not None:
            self.serializer = serializer
        super(JsonType, self).__init__(*args, **kw)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = self.serializer.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = self.serializer.loads(value)
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


def JsonDictType(serializer=None):
    """
    function which returns a SQLA Column Type suitable to store a Json dict.

    :returns: ptah.sqla.MutationDict
    """
    return MutationDict.as_mutable(JsonType(serializer=serializer))


def JsonListType(serializer=None):
    """
    function which returns a SQLA Column Type suitable to store a Json array.

    :returns: ptah.sqla.MutationList
    """
    return MutationList.as_mutable(JsonType(serializer=serializer))
