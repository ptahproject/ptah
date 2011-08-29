""" token interfaces """
from zope import interface


class ITokenType(interface.Interface):
    """ Token type interface

    ``id`` unique token type id. Token service uses this id
    for token type identification in tokens storage.

    ``timeout`` token timout, it has to be timedelta instance.
    """

    id = interface.Attribute('Unique type id')

    timeout = interface.Attribute('Token timeout')


class ITokenService(interface.Interface):
    """ Token management service """

    def generate(type, data):
        """ Generate and return string token.

        ``type`` object implemented ITokenType interface.

        ``data`` token type specific data, it must be python string. """

    def check(token, type, data=None):
        """ Check token """

    def remove(token):
        """ Remove token """
