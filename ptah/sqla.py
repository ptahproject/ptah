""" sqlalchemy query wrapper """
import ptah
import json
import sqlalchemy as sqla


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

    columns = [(name, cl) for i, name, cl in sorted(columns)]

    return build_sqla_fieldset(columns, skipPrimaryKey)


mapping = {
    (sqla.Unicode, sqla.UnicodeText, sqla.String, sqla.Text): 'text',
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
        if cl.info.get('skip', False):
            continue

        if 'field' in cl.info:
            field = cl.info['field']
            fields.append(field)
            continue

        if cl.primary_key and skipPrimaryKey:
            continue

        typ = cl.info.get('factory')
        if typ is None:
            typ = cl.info.get('field_type')

        if typ is None:
            for cls, field_type in mapping.items():
                if isinstance(cl.type, cls):
                    typ = field_type
                    break
        if typ is None:
            continue

        kwargs = {}
        for attr in ('missing', 'title', 'description',
                     'vocabulary', 'validator'):
            if attr in cl.info:
                kwargs[attr] = cl.info[attr]

        if cl.primary_key and (typ == 'int'):
            kwargs['readonly'] = True

        if callable(typ):
            field = typ(name, **kwargs)
        else:
            field = ptah.form.FieldFactory(typ, name, **kwargs)
        fields.append(field)

    return ptah.form.Fieldset(*fields)
