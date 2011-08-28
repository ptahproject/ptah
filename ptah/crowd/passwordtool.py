""" password tool """
from os import urandom
from random import randint
from codecs import getencoder
from hashlib import md5, sha1
from base64 import urlsafe_b64encode, urlsafe_b64decode

from zope import interface
from zope.component import getUtility, queryUtility

from memphis import config
from ptah.models import AuthToken
from ptah.interfaces import IAuthentication, AUTH_RESETPWD

from models import User, Session
from interfaces import _, IPasswordTool


class PlainPasswordManager(object):
    """PLAIN password manager."""

    def encode(self, password, salt=None):
        return '{plain}%s'%password

    def check(self, encoded, password):
        if encoded != password:
            return encoded == '{plain}%s'%password
        return True


class SSHAPasswordManager(object):
    """SSHA password manager."""

    _encoder = getencoder("utf-8")

    def encode(self, password, salt=None):
        if salt is None:
            salt = urandom(4)
        hash = sha1(self._encoder(password)[0])
        hash.update(salt)
        return '{ssha}' + urlsafe_b64encode(hash.digest() + salt)

    def check(self, encoded_password, password):
        # urlsafe_b64decode() cannot handle unicode input string. We
        # encode to ascii. This is safe as the encoded_password string
        # should not contain non-ascii characters anyway.
        encoded_password = encoded_password.encode('ascii')
        byte_string = urlsafe_b64decode(encoded_password[6:])
        salt = byte_string[20:]
        return encoded_password == self.encodePassword(password, salt)


class PasswordTool(object):
    """ Password management utility. """
    config.utility()
    interface.implements(IPasswordTool)

    min_length = 5
    letters_digits = False
    letters_mixed_case = False

    pm = {'{plain}': PlainPasswordManager(),
          '{ssha}': SSHAPasswordManager(),
          }

    #passwordManager = SSHAPasswordManager()
    passwordManager = PlainPasswordManager()

    def checkPassword(self, encodedPassword, password):
        for prefix, pm in self.pm.items():
            if encodedPassword.startswith(prefix):
                return pm.check(encodedPassword, password)

        return self.passwordManager.check(encodedPassword, password)

    def encodePassword(self, password, salt=None):
        return self.passwordManager.encode(password, salt)

    def getPrincipal(self, passcode):
        at = AuthToken.get(passcode, AUTH_RESETPWD)

        if at is not None:
            return getUtility(IAuthentication).getUserByLogin(at.data)

    def generatePasscode(self, principal):
        at = AuthToken(AUTH_RESETPWD, principal.login)
        Session.add(at)
        return at.token

    def resetPassword(self, passcode, password):
        at = AuthToken.get(passcode, AUTH_RESETPWD)

        if at is not None:
            principal = getUtility(IAuthentication).getUserByLogin(at.data)
            user = User.get(principal.login)
            if user is not None:
                user.password = self.encodePassword(password)
                Session.delete(at)
                return principal

    def validatePassword(self, password):
        """
        >>> import zope.interface.verify
        >>> from zope import interface, component

        >>> zope.interface.verify.verifyClass(
        ...     interfaces.IPasswordChecker, DefaultPasswordChecker)
        True

        Default password checker uses IDefaultPasswordChecker utility
        to get configuration. We use controlpanel configlet for this but
        in this code we should create it.

        >>> checker = default.DefaultPasswordChecker()
        >>> checker.min_length = 5
        >>> checker.letters_digits = False
        >>> checker.letters_mixed_case = False

        >>> zope.interface.verify.verifyObject(IPasswordChecker, checker)
        True

        >>> checker.validate('passw')

        >>> checker.validate('ps1')
        Traceback (most recent call last):
        ...
        LengthPasswordError: ...

        >>> configlet.min_length = 6
        >>> checker.validate('passw')
        Traceback (most recent call last):
        ...
        LengthPasswordError: ...

        >>> checker.validate('password')

        >>> configlet.letters_digits = True

        >>> checker.validate('password')
        Traceback (most recent call last):
        ...
        LettersDigitsPasswordError

        >>> checker.validate('66665555')
        Traceback (most recent call last):
        ...
        LettersDigitsPasswordError

        >>> checker.validate('pass5word')

        >>> configlet.letters_mixed_case = True
        >>> checker.validate('pass5word')
        Traceback (most recent call last):
        ...
        LettersCasePasswordError

        >>> checker.validate('PASS5WORD')
        Traceback (most recent call last):
        ...
        LettersCasePasswordError

        >>> checker.validate('Pass5word')

        By default password strength is always 100%

        >>> checker.passwordStrength('Pass5word')
        100.0
        """
        if len(password) < self.min_length:
            #return _('Password should be at least ${count} characters.',
            #         mapping={'count': self.min_length})
            return 'Password should be at least %s characters.'%\
                self.min_length
        elif self.letters_digits and \
                (password.isalpha() or password.isdigit()):
            return _('Password should contain both letters and digits.')
        elif self.letters_mixed_case and \
                (password.isupper() or password.islower()):
            return _('Password should contain letters in mixed case.')

    def passwordStrength(self, password):
        return 100.0
