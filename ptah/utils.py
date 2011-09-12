""" various utils """
import uuid, simplejson
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR, PickleType, String


class JSONType(PickleType):

    impl = VARCHAR
    pickler = simplejson


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


class Guid(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return uuid.uuid4().get_hex()
        return None
