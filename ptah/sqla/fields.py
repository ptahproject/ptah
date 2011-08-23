import colander
import sqlalchemy as sa
from zope import interface
from memphis import config

from interfaces import IField


@config.adapter(sa.Unicode)
@config.adapter(sa.UnicodeText)
@interface.implementer(IField)
def strNode(cl):
    return colander.Str()

@config.adapter(sa.Integer)
@interface.implementer(IField)
def intNode(cl):
    return colander.Int()

@config.adapter(sa.Date)
@interface.implementer(IField)
def dateNode(cl):
    return colander.Date()

@config.adapter(sa.DateTime)
@interface.implementer(IField)
def datetimeNode(cl):
    return colander.DateTime()

@config.adapter(sa.Boolean)
@interface.implementer(IField)
def boolNode(cl):
    return colander.Bool()


def buildSchema(table):
    nodes = []

    for cl in table.columns:
        typ = IField(cl.type, None)
        if typ is None:
            typ = colander.Str()

        node = colander.SchemaNode(
            typ, 
            name = cl.name)

        if cl.primary_key and isinstance(node.typ, colander.Int):
            node.readonly = True

        nodes.append(node)

    return config.SchemaNode(colander.Mapping(), *nodes)
