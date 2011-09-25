""" interfaces """
import translationstring
from memphis import view
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


class IURIResolver(interface.Interface):
    """ uri resolver """

    def __call__(uri):
        """ resolve uri and return context object """


class IRestServiceAction(object):
    """ simple rest service action """

    name = interface.Attribute('Name')

    title = interface.Attribute('Action title')

    description = interface.Attribute('Action description')

    def __call__(request, *args):
        """ execute action """


class IPrincipal(interface.Interface):
    """ principal """

    uuid = interface.Attribute('Unique principal uuid')

    name = interface.Attribute('Human readable principal name')

    login = interface.Attribute('Principal login')


class IPasswordChanger(interface.Interface):
    """ principal password changer """

    def __call__(principal, password):
        """ change password """


class IAuthInfo(interface.Interface):
    """ auth info """

    uuid = interface.Attribute('Principal UUID')

    status = interface.Attribute('Status of authentication call')

    message = interface.Attribute('Failed message')

    keywords = interface.Attribute('Additional arguments from provider')

    principal = interface.Attribute('Principal object')


class IAuthentication(interface.Interface):
    """ authentication utility """

    def isAnonymous():
        """ """

    def getPrincipalByLogin(login):
        """ """

    def setUserId(uuid):
        """ set current user """

    def getUserId():
        """ get current user """

    def getCurrentPrincipal():
        """ """

    def authenticate(credentials):
        """ authenticate credentials """

    def checkPrincipalAuth(principal):
        """ check principal auth restrictions """


class IAuthChecker(interface.Interface):
    """ it is possible to perform additional checks on principal
    during authentication process"""

    def __call__(principal, authInfo):
        """ perform additional check """


class IAuthProvider(interface.Interface):
    """ auth provider """

    def getPrincipal(uuid):
        """ return principal """

    def getPrincipalByLogin(login):
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

    __owner__ = interface.Attribute('Owner')


class ILocalRolesAware(interface.Interface):
    """ local roles aware context """

    __local_roles__ = interface.Attribute('Local roles dict')


class IACLsAware(interface.Interface):
    """ acl maps aware context """

    __acls__ = interface.Attribute('List of acl map ids')
