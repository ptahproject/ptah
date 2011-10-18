""" password tool """
from os import urandom
from random import randint
from codecs import getencoder
from hashlib import sha1
from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import timedelta

from zope import interface
from ptah import config, form

import ptah
from ptah import token

from settings import PTAH_CONFIG
from interfaces import _, IPasswordTool


TOKEN_TYPE = token.TokenType(
    '35c9b7df958f4e93ae9b275a7dc2219e', timedelta(minutes=10))


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
        return encoded_password == self.encode(password, salt)


class PasswordTool(object):
    """ Password management utility. """
    interface.implements(IPasswordTool)

    min_length = 5
    letters_digits = False
    letters_mixed_case = False

    pm = {'{plain}': PlainPasswordManager(),
          '{ssha}': SSHAPasswordManager(),
          }
    passwordManager = pm['{plain}']

    def __init__(self):
        self._changers = {}

    def check(self, encoded, password):
        try:
            pm, pwd = encoded.split('}', 1)
        except:
            return self.passwordManager.check(encoded, password)

        manager = self.pm.get('%s}'%pm)
        if manager is not None:
            return manager.check(encoded, password)
        return False

    def encode(self, password, salt=None):
        return self.manager.encode(password, salt)

    def registerPasswordChanger(self, typ, changer):
        self._changers[typ] = changer

    def hasPasswordChanger(self, uri):
        return ptah.extract_uri_schema(uri) in self._changers

    def getPrincipal(self, passcode):
        data = token.service.get(passcode)

        if data is not None:
            return ptah.resolve(data)

    def generatePasscode(self, uri):
        return token.service.generate(TOKEN_TYPE, uri)

    def removePasscode(self, passcode):
        token.service.remove(passcode)

    def changePassword(self, passcode, password):
        principal = self.getPrincipal(passcode)

        self.removePasscode(passcode)

        if principal is not None:
            changer = self._changers.get(ptah.extract_uri_schema(principal.uri))
            if changer is not None:
                changer(principal, self.encode(password))
                return True

        return False

    def validatePassword(self, password):
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


passwordTool = PasswordTool()


def passwordValidator(field, appstruct):
    err = passwordTool.validatePassword(appstruct)
    if err is not None:
        raise form.Invalid(field, err)


def passwordSchemaValidator(field, appstruct):
    if appstruct['password'] and appstruct['confirm_password']:
        if appstruct['password'] != appstruct['confirm_password']:
            raise form.Invalid(
                field, _("Password and Confirm Password should be the same."))

        passwordValidator(field, appstruct['password'])


PasswordSchema = form.Fieldset(

    form.FieldFactory(
        'password',
        'password',
        title = _(u'Password'),
        description = _(u'Enter password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        default = u''),

    form.FieldFactory(
        'password',
        'confirm_password',
        title = _(u'Confirm password'),
        description = _(u'Re-enter the password. '
                        u'Make sure the passwords are identical.'),
        default = u''),

    validator = passwordSchemaValidator
)


@config.subscriber(config.SettingsInitializing)
def initializing(ev):
    mng = PasswordTool.pm.get(PTAH_CONFIG.pwdmanager)
    if mng is None:
        mng = PasswordTool.pm.get('{%s}'%PTAH_CONFIG.pwdmanager)

    if mng is None:
        mng = PasswordTool.pm['{plain}']

    passwordTool.manager = mng
