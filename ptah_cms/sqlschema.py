import colander
import sqlalchemy as sqla
from zope import interface
from memphis import config


def generateSchema(model, schemaNodes = None, skipPrimaryKey=True):
    if '__tablename__' not in model.__dict__:
        return

    table = model.__mapper__.local_table
    return buildSchema(table, schemaNodes, skipPrimaryKey)


class IField(interface.Interface):
    pass

@config.adapter(sqla.Unicode)
@config.adapter(sqla.UnicodeText)
@interface.implementer(IField)
def strNode(cl):
    return colander.Str()

@config.adapter(sqla.Integer)
@interface.implementer(IField)
def intNode(cl):
    return colander.Int()

@config.adapter(sqla.Float)
@interface.implementer(IField)
def intNode(cl):
    return colander.Float()

@config.adapter(sqla.Date)
@interface.implementer(IField)
def dateNode(cl):
    return colander.Date()

@config.adapter(sqla.DateTime)
@interface.implementer(IField)
def datetimeNode(cl):
    return colander.DateTime()

@config.adapter(sqla.Boolean)
@interface.implementer(IField)
def boolNode(cl):
    return colander.Bool()


def buildSchema(table, schemaNodes=None, skipPrimaryKey=False):
    nodes = []

    for cl in table.columns:
        if schemaNodes is not None and cl.name not in schemaNodes:
            continue

        if 'node' in cl.info:
            node = cl.info['node']
            if not node.name:
                node.name = cl.name
            nodes.append(node)
            continue
        
        if cl.primary_key and skipPrimaryKey:
            continue

        if 'type' in cl.info:
            tp = cl.info['type']
        else:
            tp = cl.type

        typ = IField(tp, None)
        if typ is None:
            node = colander.SchemaNode(colander.Str(), name = cl.name)
        if type(typ) is tuple:
            node = colander.SchemaNode(typ[0], typ[1], name = cl.name)
        else:
            node = colander.SchemaNode(typ, name = cl.name)

        for name in ('missing', 'title', 'description',
                     'widget', 'vocabulary'):
            if name in cl.info:
                setattr(node, name, cl.info[name])

        if cl.primary_key and isinstance(node.typ, colander.Int):
            node.readonly = True

        nodes.append(node)

    return config.SchemaNode(colander.Mapping(), *nodes)
