"""Widget Framework Implementation"""
import colander
from zope import interface
from memphis import config
from memphis.form.interfaces import IDataManager, IFieldDataManager


class DataManager(object):
    interface.implements(IDataManager)
    config.adapter(interface.Interface)

    def __init__(self, default):
        self.datasets = {'': IFieldDataManager(default)}
    
    def append(self, name, data):
        self.datasets[name] = IFieldDataManager(data)

    def dataset(self, name):
        return self.datasets[name]


class AttributeField(object):
    """Attribute field."""
    interface.implements(IFieldDataManager)
    config.adapter(interface.Interface)

    def __init__(self, context):
        self.context = context

    def get(self, node):
        return getattr(self.context, node.name)

    def query(self, node, default=colander.null):
        try:
            return self.get(node)
        except AttributeError:
            return default


_marker = object()

class DictionaryField(object):
    """Dictionary field."""
    interface.implements(IFieldDataManager)
    config.adapter(dict)

    def __init__(self, data):
        if not isinstance(data, dict):
            raise ValueError("Data are not a dictionary: %s" %type(data))
        self.data = data

    def get(self, node):
        value = self.data.get(node.name, _marker)
        if value is _marker:
            raise AttributeError
        return value

    def query(self, node, default=colander.null):
        return self.data.get(node.name, default)
