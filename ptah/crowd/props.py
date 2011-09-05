"""  """
import colander
from zope import interface
from memphis import config

from interfaces import IPreferencesGroup
from models import Session, UserProps

userPropsSchema = colander.SchemaNode(
    colander.Mapping(),

    colander.SchemaNode(
        colander.DateTime(),
        name = 'date',
        required = False),

    colander.SchemaNode(
        colander.Str(),
        name = 'title',
        missing = ''),

    name = 'userprops',
    title = 'User props',
)


class Props(object):
    interface.implements(IPreferencesGroup)
    config.utility(name='userprops')

    name = 'userprops'
    schema = userPropsSchema

    def get(self, id):
        return UserProps.get(id)

    def update(self, id, **kwargs):
        up = UserProps.get(id)
        if up is not None:
            for k, v in kwargs.items():
                setattr(up, k, v)

    def create(self, id, **kwargs):
        uprops = UserProps(id)
        for attr, val in kwargs.items():
            setattr(uprops, attr, val)

        Session.add(uprops)
