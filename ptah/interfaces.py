""" interfaces """
import translationstring
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


class IURIResolver(interface.Interface):
    """ uri resolver """

    def __call__(uri):
        """ resolve uri and return context object """


class Principal(object):
    """ Principal interface """

    #: Principal uri
    __uri__ = ''

    #: Principal name
    name = ''

    #: Principal login
    login = ''


class AuthInfo(object):
    """ Authentication information """

    #: Principal uri or None if principal is not set
    __uri__ = None

    #: :py:class:`ptah.interfaces.Principal` object
    principal = None

    #: Status, True is principal has been authenticated, false otherwise
    status = False

    #: Extra readable message from auth checkers
    message = False


class AuthChecker(interface.Interface):
    """ it is possible to perform additional checks on principal
    during authentication process"""

    def __call__(principal, authInfo):
        """ perform principal check """


class AuthProvider(object):
    """ Authentication provider interface """

    def authenticate(self, credentials):
        """ Authenticate credentials,
        return `ptah.interfaces.Principal` object """

    def get_principal_bylogin(self, login):
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
