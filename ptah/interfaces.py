""" interfaces """
import translationstring
from zope import interface
from memphis import view

_ = translationstring.TranslationStringFactory('ptah')


AUTH_RESETPWD = 1


class IAuthentication(interface.Interface):
    """ authentication service """

    def isAnonymous():
        """ check if current use is anonymous """

    def authenticate(credentials):
        """ authenticate credentials """

    def getUserByLogin(login):
        """ return user by login """


class IPtahRoute(interface.Interface):
    """ ptah route """


class IPtahManageRoute(view.INavigationRoot):
    """ user management route """


class IPtahModule(interface.Interface):
    """ module """

    name = interface.Attribute('Module name')
    title = interface.Attribute('Module title')

    def url(request):
        """ return url to this module """

    def bind(manager, request):
        """ bind module to context """

    def available(request):
        """ is module available """
