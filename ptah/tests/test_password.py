import unittest
import ptah
from ptah import form

from base import Base


class TestPasswordSchema(Base):

    def test_password_required(self):
        self._init_ptah()
        from ptah.password import PasswordSchema

        pwdSchema = PasswordSchema.bind(params={})

        data, errors = pwdSchema.extract()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].field.name, 'password')

    def test_password_equal(self):
        self._init_ptah()
        from ptah.password import PasswordSchema

        pwdSchema = PasswordSchema.bind(
            params={'password': '12345', 'confirm_password': '123456'})
        data, errors = pwdSchema.extract()

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0].field, form.Fieldset)
        self.assertEqual(
            errors[0].msg[0],
            "Password and Confirm Password should be the same.")

    def test_password(self):
        self._init_ptah()
        from ptah.password import PasswordSchema

        pwdSchema = PasswordSchema.bind(
            params={'password': '12345', 'confirm_password': '12345'})
        data, errors = pwdSchema.extract()
        self.assertEqual(len(errors), 0)

    def test_password_validator(self):
        from ptah.password import passwordValidator, PasswordTool

        vp = PasswordTool.validatePassword

        def validatePassword(self, pwd):
            return 'Error'

        PasswordTool.validatePassword = validatePassword

        self.assertRaises(
            form.Invalid, passwordValidator, None, 'pwd')
        
        PasswordTool.validatePassword = vp


class TestSHAPasswordManager(unittest.TestCase):

    def test_password_ssha(self):
        from ptah.password import SSHAPasswordManager

        manager = SSHAPasswordManager()
        
        password = u"right \N{CYRILLIC CAPITAL LETTER A}"
        encoded = manager.encode(password, salt="")

        self.assertEqual(encoded, '{ssha}BLTuxxVMXzouxtKVb7gLgNxzdAI=')
        self.assertTrue(manager.check(encoded, password))
        self.assertFalse(manager.check(encoded, password + u"wrong"))

        encoded = manager.encode(password)
        self.assertTrue(manager.check(encoded, password))       


class TestPasswordSettings(Base):

    def test_password_settings(self):
        from ptah.password import \
             initializing, PlainPasswordManager, SSHAPasswordManager
        
        ptah.PTAH_CONFIG['pwdmanager'] = 'unknown'
        initializing(None)

        self.assertIsInstance(ptah.passwordTool.manager, PlainPasswordManager)

        ptah.PTAH_CONFIG['pwdmanager'] = 'ssha'
        initializing(None)

        self.assertIsInstance(ptah.passwordTool.manager, SSHAPasswordManager)


class TestPasswordTool(Base):

    def test_password_encode(self):
        from ptah.password import PasswordTool
        
        ptah.passwordTool.manager = PasswordTool.pm['{plain}']

        encoded = ptah.passwordTool.encode('12345')
        self.assertEqual(encoded, '{plain}12345')

    def test_password_check(self):
        from ptah.password import PasswordTool
        ptah.passwordTool.manager = PasswordTool.pm['{ssha}']

        self.assertTrue(ptah.passwordTool.check('12345', '12345'))
        self.assertTrue(ptah.passwordTool.check('{plain}12345', '12345'))
        self.assertFalse(ptah.passwordTool.check('{plain}12345', '123455'))
        self.assertFalse(ptah.passwordTool.check('{unknown}12345', '123455'))
