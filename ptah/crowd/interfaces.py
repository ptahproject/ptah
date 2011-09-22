""" crowd interfaces """
import ptah
import translationstring
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


class IPreferencesPanel(interface.Interface):
    """ preferences panel """


class IPreferencesGroup(interface.Interface):
    """ preferences group """

    id = interface.Attribute('Unique pref id')

    schema = interface.Attribute('Colander schema')

    def get(id):
        """ Return preferences for principal.

        method returns dictionary. """

    def update(id, **kwargs):
        """ update preferences """


class IPrincipalWithEmail(ptah.IPrincipal):
    """ principal with email """

    email = interface.Attribute('Principal email')
