""" crowd interfaces """
import ptah
import translationstring
from zope import interface
from memphis import config

_ = translationstring.TranslationStringFactory('ptah')


class ICrowdModule(ptah.IPtahModule):
    """ marker interface for crowd module """


class ICrowdUser(interface.Interface):
    """ wrapper for actual user """

    user = interface.Attribute('Wrapped user object')


class IPreferencesPanel(interface.Interface):
    """ preferences panel """


class IAction(interface.Interface):
    """ ptah action """

    title = interface.Attribute('User friendly title')

    action = interface.Attribute('Action')

    def available(principal):
        """ check if action is availble for principal """


class IManageUserAction(IAction):
    """ user management action """


class IPersonalAction(IAction):
    """ user preferences action """


class IPreferencesGroup(interface.Interface):
    """ preferences group """

    id = interface.Attribute('Unique pref id')

    schema = interface.Attribute('Colander schema')

    def get(id):
        """ Return preferences for principal.

        method returns dictionary. """

    def update(id, **kwargs):
        """ update preferences """
