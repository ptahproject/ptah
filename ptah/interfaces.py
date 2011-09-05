""" interfaces """
import translationstring
from zope import interface
from memphis import view

_ = translationstring.TranslationStringFactory('ptah')


class IPrincipal(interface.Interface):
    """ principal """

    id = interface.Attribute('Unique principal id')

    name = interface.Attribute('Human readable principal name')

    login = interface.Attribute('Principal login')


class IAuthenticationPlugin(interface.Interface):
    """ auth plugin """

    def authenticate(credentials):
        """ authenticate credentials """

    def isAnonymous():
        """ check if current use is anonymous """
    
    def getPrincipal(id):
        """ return principal object for id """

    def getCurrentUser(id):
        """ return user by login """

    def getUserByLogin(login):
        """ return user by login """

IAuthentication = IAuthenticationPlugin


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
