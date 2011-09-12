""" user events """
from memphis import config


class PrincipalEvent(object):
    """ base class for all principal related events """

    principal = None # IPrincipal object

    def __init__(self, principal):
        self.principal = principal


class LoggedInEvent(PrincipalEvent):
    """ User logged in to system."""
    config.event('Logged in event')


class LogingFailedEvent(object):
    """ User loging failed."""
    config.event('Loging failed event')

    login = None # Login

    def __init__(self, login):
        self.login = login


class ResetPasswordInitiatedEvent(PrincipalEvent):
    """ User has initiated password changeing."""
    config.event('Reset password initiated event')


class ValidatedEvent(PrincipalEvent):
    """ User account has been validated."""
    config.event('Account validation event')


class UserAddedEvent(PrincipalEvent):
    """ User added event """


class UserRegisteredEvent(UserAddedEvent):
    """ User registered event """
