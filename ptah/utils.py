""" various utils """
import uuid, simplejson
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR


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
