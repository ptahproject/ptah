"""Widget Framework Implementation"""
import colander
from zope import interface
from memphis import config
from memphis.form.interfaces import IDataManager


class AttributeField(object):
    """Attribute field."""
    interface.implements(IDataManager)
    config.adapts(interface.Interface, colander.SchemaNode)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def get(self):
        return getattr(self.context, self.field.name)

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

    def __init__(self, data, field):
        if not isinstance(data, dict):
            raise ValueError("Data are not a dictionary: %s" %type(data))
        self.data = data
        self.field = field

    def get(self):
        value = self.data.get(self.field.name, _marker)
        if value is _marker:
            raise AttributeError
        return value

    def query(self, default=colander.null):
        return self.data.get(self.field.name, default)
