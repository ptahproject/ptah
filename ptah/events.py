from ptah import config


class PrincipalEvent(object):
    """ base class for all principal related events """

    principal = None  # IPrincipal object

    def __init__(self, principal):  # pragma: no cover
        self.principal = principal


class LoggedInEvent(PrincipalEvent):
    """ User logged in to system."""
    config.event('Logged in event')


class LoginFailedEvent(PrincipalEvent):
    """ User login failed."""
    config.event('Login failed event')

    message = ''

    def __init__(self, principal, message=u''):  # pragma: no cover
        self.principal = principal
        self.message = message


class LoggedOutEvent(PrincipalEvent):
    """ User logged out."""
    config.event('Logged out event')


class ResetPasswordInitiatedEvent(PrincipalEvent):
    """ User has initiated password changeing."""
    config.event('Reset password initiated event')


class PrincipalPasswordChangedEvent(PrincipalEvent):
    """ User password has been changed. """
    config.event('User password has been changed')


class PrincipalValidatedEvent(PrincipalEvent):
    """ Principal account has been validated."""
    config.event('Account validation event')


class PrincipalAddedEvent(PrincipalEvent):
    """ Principal added event """


class PrincipalRegisteredEvent(PrincipalEvent):
    """ Principal registered event """
