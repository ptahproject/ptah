from memphis import form

from base import Base


class TestPasswordSchema(Base):

    def test_password_required(self):
        self._init_memphis()
        from ptah.password import PasswordSchema

        pwdSchema = PasswordSchema.bind(params={})

        data, errors = pwdSchema.extract()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].field.name, 'password')

    def test_password_equal(self):
        self._init_memphis()
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
        self._init_memphis()
        from ptah.password import PasswordSchema

        pwdSchema = PasswordSchema.bind(
            params={'password': '12345', 'confirm_password': '12345'})
        data, errors = pwdSchema.extract()
        self.assertEqual(len(errors), 0)
