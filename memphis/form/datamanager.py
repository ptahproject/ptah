"""Widget Framework Implementation"""
import colander
from zope import interface
from memphis import config
from memphis.form.interfaces import IDataManager


class AttributeField(object):
    """Attribute field."""
    interface.implements(IDataManager)
    config.adapts(interface.Interface, colander.SchemaNode)

    def __init__(self, context, node):
        self.context = context
        self.node = node

    def get(self):
        return getattr(self.context, self.node.name)

    def query(self, default=colander.null):
        try:
            return self.get()
        except AttributeError:
            return default


_marker = object()

class DictionaryField(object):
    """Dictionary field."""
    interface.implements(IDataManager)
    config.adapts(dict, colander.SchemaNode)

    def __init__(self, data, node):
        if not isinstance(data, dict):
            raise ValueError("Data are not a dictionary: %s" %type(data))
        self.data = data
        self.node = node

    def get(self):
        value = self.data.get(self.node.name, _marker)
        if value is _marker:
            raise AttributeError
        return value

    def query(self, default=colander.null):
        return self.data.get(self.node.name, default)
