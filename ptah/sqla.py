""" sqlalchemy query wrapper """
import simplejson
from ptah import form
from threading import local

import sqlalchemy as sqla
from sqlalchemy import orm
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR


class QueryFreezer(object):
    """ A facade for sqla.Session.query which caches internal query structure.

    :param builder: anonymous function containing SQLAlchemy query

    .. code-block:: python

        _sql_parent = ptah.QueryFreezer(
            lambda: Session.query(Content)
                .filter(Content.__uri__ == sqla.sql.bindparam('parent')))
    """

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


def get_columns_order(mapper):
    if mapper.inherits is not None:
        order = get_columns_order(mapper.inherits)
    else:
        order = []

    table = mapper.local_table
    for cl in table.columns:
        order.append((table.name, cl.name))

    return order


def generate_fieldset(model, fieldNames=None, namesFilter=None,
                      skipPrimaryKey=True):
    """
    :param model: subclass of sqlalchemy.ext.declarative.declarative_base
    :param fieldNames: **optional** sequence of strings to use
    :param namesFilter: **optional** callable which takes a key and list
        of fieldNames to compute if fieldName should filtered out of Fieldset
        generation.
    :param skipPrimaryKey: **default: True** Should PrimaryKey be omitted
        from fieldset generation.
    :returns: a instance of :py:class:`ptah.form.Fieldset`
    """
    mapper = model.__mapper__
    order = get_columns_order(mapper)

    columns = []
    for attr in list(mapper.class_manager.attributes):
        cl = attr.__clause_element__()
        if isinstance(cl, sqla.Column):
            if fieldNames is not None and attr.key not in fieldNames:
                continue

            if namesFilter is not None and \
                    not namesFilter(attr.key, fieldNames):
                continue

            idx = order.index((cl.table.name, cl.name))
            columns.append((idx, attr.key, cl))

    columns.sort()
    columns = [(name, cl) for i, name, cl in columns]

    return build_sqla_fieldset(columns, skipPrimaryKey)


mapping = {
    (sqla.Unicode, sqla.UnicodeText, sqla.String): 'text',
    sqla.Integer: 'int',
    sqla.Float: 'float',
    sqla.Date: 'date',
    sqla.DateTime: 'datetime',
    sqla.Boolean: 'bool',
}


def build_sqla_fieldset(columns, skipPrimaryKey=False):
    """
    Given a list of SQLAlchemy columns generate a ptah.form.Fieldset.

    :param columns: sequence of sqlachemy.schema.Column instances
    :param skipPrimaryKey: **default: False** boolean whether to include PK
      Columns in Fieldset generation.
    :returns: a instance of :py:class:`ptah.form.Fieldset`
    """
    fields = []

    for name, cl in columns:
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

        kwargs = {}
        for attr in ('missing', 'title', 'description', 'vocabulary'):
            if attr in cl.info:
                kwargs[attr] = cl.info[attr]

        if cl.primary_key and (typ == 'int'):
            kwargs['readonly'] = True

        field = form.FieldFactory(typ, name, **kwargs)
        fields.append(field)

    return form.Fieldset(*fields)
