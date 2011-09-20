""" interfaces """
import translationstring
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


class IPrincipal(interface.Interface):
    """ principal """

    uuid = interface.Attribute('Unique principal uuid')

    name = interface.Attribute('Human readable principal name')

    login = interface.Attribute('Principal login')


class IPrincipalWithEmail(IPrincipal):
    """ principal with email """

    email = interface.Attribute('Principal email')


class IPasswordChanger(interface.Interface):
    """ principal password changer """

    def __call__(principal, password):
        """ change password """


class IAuthInfo(interface.Interface):
    """ auth info """

    status = interface.Attribute('Status of authentication call')

    message = interface.Attribute('Failed message')

    keywords = interface.Attribute('Additional arguments from provider')

    principal = interface.Attribute('Principal object')

    uuid = interface.Attribute('Principal UUID')


class IAuthentication(interface.Interface):
    """ authentication utility """

    def isAnonymous():
        """ """

    def getPrincipalByLogin(login):
        """ """

    def getCurrentPrincipal():
        """ """

    def authenticate(credentials):
        """ authenticate credentials """


class IAuthChecker(interface.Interface):
    """ it is possible to perform additional checks on principal 
    during authentication process"""

    def __call__(principal, authInfo):
        """ perform additional check """


class IAuthProvider(interface.Interface):
    """ auth provider """

    def getPrincipalInfo(id):
        """ return principal object for id """

    def getPrincipalInfoByLogin(login):
        """ return principal object """

    def authenticate(credentials):
        """ authenticate credentials """


class IPrincipalSearcher(interface.Interface):
    """ auth provider with search support """

    def __call__(term=''):
        """ search users return IPrincipal object """


class IPasswordTool(interface.Interface):
    """ password tool """

    min_length = interface.Attribute('Minimum length')
    letters_digits = interface.Attribute(u'Letters and digits')
    letters_mixed_case = interface.Attribute(u'Letters case')

    def encodePassword(password, *args, **kw):
        """ encode password """

    def checkPassword(encodedPassword, password):
        """ check password """

    def validatePassword(password):
        """ validate password """

    def passwordStrength(password):
        """ check password strength """

    def getPrincipal(passcode):
        """ return principal by passcode """

    def removePasscode(passcode):
        """ remove passcode """

    def generatePasscode(principal):
        """ generate passcode for principal """


class IOwnersAware(interface.Interface):
    """ owners aware context """

    __owners__ = interface.Attribute('Owners list')


class ILocalRolesAware(interface.Interface):
    """ local roles aware context """

    __local_roles__ = interface.Attribute('Local roles dict')
