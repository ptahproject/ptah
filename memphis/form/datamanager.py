"""Widget Framework Implementation"""
import colander
from zope import interface
from memphis import config
from memphis.form import interfaces

_marker = []


class AttributeField(object):
    """Attribute field."""
    interface.implements(interfaces.IDataManager)
    config.adapts(interface.Interface, colander.SchemaNode)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def get(self):
        return self.field.get(self.context)

    def query(self, default=interfaces.NO_VALUE):
        try:
            return self.get()
        except AttributeError:
            return default

    def set(self, value):
        context = self.adapted_context
        field = self.field.bind(context)
        field.set(context, value)


class DictionaryField(object):
    """Dictionary field.

    NOTE: Even though, this data manager allows nearly all kinds of
    mappings, by default it is only registered for dict, because it
    would otherwise get picked up in undesired scenarios. If you want
    to it use for another mapping, register the appropriate adapter in
    your application.
    """
    interface.implements(interfaces.IDataManager)
    config.adapts(dict, colander.SchemaNode)

    _allowed_data_classes = (dict,)

    def __init__(self, data, field):
        if (not isinstance(data, self._allowed_data_classes) and
            not mapping.IMapping.providedBy(data)):
            raise ValueError("Data are not a dictionary: %s" %type(data))
        self.data = data
        self.field = field

    def get(self):
        value = self.data.get(self.field.name, _marker)
        if value is _marker:
            raise AttributeError
        return value

    def query(self, default=interfaces.NO_VALUE):
        return self.data.get(self.field.name, default)

    def set(self, value):
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields name=%s"
                            % self.field.__name__)
        self.data[self.field.name] = value
