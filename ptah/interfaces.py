""" interfaces """
import translationstring
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


class IURIResolver(interface.Interface):
    """ uri resolver """

    def __call__(uri):
        """ resolve uri and return context object """


class IPrincipal(interface.Interface):
    """ principal """

    uri = interface.Attribute('Unique principal id')

    name = interface.Attribute('Human readable principal name')

    login = interface.Attribute('Principal login')


class IPasswordChanger(interface.Interface):
    """ principal password changer """

    def __call__(principal, password):
        """ change password """


class IAuthInfo(interface.Interface):
    """ auth info """

    uri = interface.Attribute('Principal UUID')

    status = interface.Attribute('Status of authentication call')

    message = interface.Attribute('Failed message')

    keywords = interface.Attribute('Additional arguments from provider')

    principal = interface.Attribute('Principal object')


class IAuthentication(interface.Interface):
    """ authentication utility """

    def authenticate(credentials):
        """ authenticate credentials """

    def authenticate_principal(principal):
        """ check principal restrictions """

    def set_userid(uri):
        """ set current user """

    def get_userid():
        """ get current user """

    def get_current_principal():
        """ """

    def get_principal_bylogin(login):
        """ """


class IAuthChecker(interface.Interface):
    """ it is possible to perform additional checks on principal
    during authentication process"""

    def __call__(principal, authInfo):
        """ perform principal check """


class IAuthProvider(interface.Interface):
    """ auth provider """

    def authenticate(credentials):
        """ authenticate credentials """

    def get_principal_bylogin(login):
        """ return principal object """


class IPrincipalSearcher(interface.Interface):
    """ auth provider with search support """

    def __call__(term=''):
        """ search users return IPrincipal object """


class IOwnersAware(interface.Interface):
    """ owners aware context """

    __owner__ = interface.Attribute('Owner')


class ILocalRolesAware(interface.Interface):
    """ local roles aware context """

    __local_roles__ = interface.Attribute('Local roles dict')


class IACLsAware(interface.Interface):
    """ acl maps aware context """

    __acls__ = interface.Attribute('List of acl map ids')


class IIntrospection(interface.Interface):
    """ introspection handler """

    name = interface.Attribute('Name')
    title = interface.Attribute('Title')

    def __init__(request):
        """ constructor """

    def renderAction(action):
        """ render config actions """

    def renderActions(*actions):
        """ render config actions """
