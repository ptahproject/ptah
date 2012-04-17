""" interfaces """
import translationstring
from zope import interface
from pyramid.httpexceptions import HTTPForbidden, HTTPNotFound

_ = translationstring.TranslationStringFactory('ptah')


def resolver(uri):
    """Resolve uri to object.

    :param uri: Uri string
    :rtype: Resolved object
    """


class Principal(object):
    """ Principal interface

    .. attribute:: __uri__

       Principal uri

    .. attribute:: name

       Principal name

    .. attribute:: login

       Principal login

    """


class AuthInfo(object):
    """ Authentication information

    .. attribute:: __uri__

       Principal uri or None if principal is not set

    .. attribute:: principal

       :py:class:`ptah.interfaces.Principal` object

    .. attribute:: status

       Status, True is principal has been authenticated, false otherwise

    .. attribute:: message

       Readable message from auth checkers

    """


def auth_checker(info):
    """ Perform additional checks on principal during authentication process.

    :param info: A instance of :py:class:`ptah.interfaces.AuthInfo` class
    """


class AuthProvider(object):
    """ Authentication provider interface """

    def authenticate(self, credentials):
        """ Authenticate credentials,
        return :py:class:`ptah.interfaces.Principal` object or None """

    def get_principal_bylogin(self, login):
        """ return instance of :py:class:`ptah.interfaces.Principal` of None """


def principal_searcher(term):
    """ Search users by term

    :param term: search term (str)
    :rtype: iterator of :py:class:`ptah.interfaces.Principal` instances

    """

class IOwnersAware(interface.Interface):
    """ Owners aware context

    .. attribute:: __owner__

       Owner principal uri
    """

    __owner__ = interface.Attribute('Owner')


class ILocalRolesAware(interface.Interface):
    """ Local roles aware context

    .. attribute:: __local_roles__

    """

    __local_roles__ = interface.Attribute('Local roles dict')


class IACLsAware(interface.Interface):
    """ acl maps aware context """

    __acls__ = interface.Attribute('List of acl map ids')


def populate_step(registry):
    """ Populate data step.

    :param registry: Pyramid :py:class:`pyramid.registry.Registry` object
    """


def roles_provider(context, uid, registry):
    """ Roles provider interface

    :param context: Current context object
    :param userid: User id
    :param registry: Pyramid registry object
    :rtype: Sequence of roles
    """


class TypeException(Exception):
    """ type exception """


class Forbidden(HTTPForbidden, TypeException):
    """ something is forbidden """


class NotFound(HTTPNotFound, TypeException):
    """ something is not found """


class ITypeInformation(interface.Interface):
    """ Content type information """

    name = interface.Attribute('Name')
    title = interface.Attribute('Title')
    description = interface.Attribute('Description')

    permission = interface.Attribute('Add permission')

    filter_content_types = interface.Attribute('Filter addable types')
    allowed_content_types = interface.Attribute('List of addable types')
    global_allow = interface.Attribute('Addable globally')

    def create(**data):
        """ construct new content instance """

    def is_allowed(container):
        """ allow create this content in container """

    def check_context(container):
        """ same as isAllowed, but raises HTTPForbidden """

    def list_types(self, container):
        """ list addable content types """
