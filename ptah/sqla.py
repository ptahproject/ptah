""" sqlalchemy query wrapper """
import simplejson
from memphis import form
from threading import local

import sqlalchemy as sqla
from sqlalchemy import orm
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR


class QueryFreezer(object):

    def __init__(self, builder):
        self.builder = builder
        self.data = local()

    def reset(self):
        self.data = local()

    def iter(self, **params):
        data = self.data
        if not hasattr(data, 'query'):
            data.query = self.builder()
            data.mapper = data.query._mapper_zero_or_none()
            data.querycontext = data.query._compile_context()
            data.querycontext.statement.use_labels = True
            data.stmt = data.querycontext.statement

        conn = data.query._connection_from_session(
            mapper = data.mapper,
            clause = data.stmt,
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

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = simplejson.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = simplejson.loads(value)
        return value


class MutationList(Mutable, list):

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationList):
            if isinstance(value, list):
                return MutationList(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def append(self, value):
        list.append(self, value)
        self.changed()

    def __setitem__(self, key, value):
        list[key] = value
        self.changed()

    def __delitem__(self, key):
        del list[key]
        self.changed()


class MutationDict(Mutable, dict):

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationDict):
            if isinstance(value, dict):
                return MutationDict(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()


def JsonDictType():
    return MutationDict.as_mutable(JsonType)


def JsonListType():
    return MutationList.as_mutable(JsonType)


def generateFieldset(model, fieldNames = None, skipPrimaryKey=True):
    if '__tablename__' not in model.__dict__:
        return

    table = model.__mapper__.local_table
    return buildSqlaFieldset(table, fieldNames, skipPrimaryKey)


mapping = {
    (sqla.Unicode, sqla.UnicodeText, sqla.String): 'text',
    sqla.Integer: 'int',
    sqla.Float: 'float',
    sqla.Date: 'date',
    sqla.DateTime: 'datetime',
    sqla.Boolean: 'bool',
}


def buildSqlaFieldset(table, fieldNames=None, skipPrimaryKey=False):
    fields = []

    for cl in table.columns:
        if fieldNames is not None and cl.name not in fieldNames:
            continue

        if 'field' in cl.info:
            field = cl.info['field']
            fields.append(field)
            continue

        if cl.primary_key and skipPrimaryKey:
            continue

        typ = cl.info.get('field_type')
        if typ is None:
            for cls, field_type in mapping.items():
                if isinstance(cl.type, cls):
                    typ = field_type
                    break
        if typ is None:
            continue

        field = form.FieldFactory(typ, name = cl.name)

        for name in ('missing', 'title', 'description',
                     'widget', 'vocabulary'):
            if name in cl.info:
                setattr(field, name, cl.info[name])

        if cl.primary_key and (typ == 'int'):
            field.readonly = True

        fields.append(field)

    return form.Fieldset(*fields)
