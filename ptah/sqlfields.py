import sqlalchemy as sqla
from memphis import form


def generateFieldset(model, fieldNames = None, skipPrimaryKey=True):
    if '__tablename__' not in model.__dict__:
        return

    table = model.__mapper__.local_table
    return buildFields(table, fieldNames, skipPrimaryKey)


mapping = {
    sqla.Unicode: 'text',
    sqla.UnicodeText: 'text',
    sqla.Integer: 'int',
    sqla.Float: 'float',
    sqla.Date: 'date',
    sqla.DateTime: 'datetime',
    sqla.Boolean: 'bool',
}


def buildFields(table, fieldNames=None, skipPrimaryKey=False):
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
