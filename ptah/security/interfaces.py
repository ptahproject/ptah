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


class IAuthentication(interface.Interface):
    """ authentication """

    def isAnonymous():
        """ """

    def getPrincipalByLogin(login):
        pass

    def getCurrentPrincipal():
        pass

    def authenticate(credentials):
        """ authenticate credentials """


class IAuthProvider(interface.Interface):
    """ auth provider """

    def getPrincipalInfo(id):
        """ return principal object for id """

    def getPrincipalInfoByLogin(login):
        """ return principal object """

    def authenticate(credentials):
        """ authenticate credentials """


class ISearchableAuthProvider(interface.Interface):
    """ auth provider with search support """

    def search(term=''):
        """ search users return id, name, login """


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
