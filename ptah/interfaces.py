""" interfaces """
import translationstring
from zope import interface

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
