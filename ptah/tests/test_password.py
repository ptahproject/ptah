
from base import Base


class TestPasswordSchema(Base):

    def test_password_schema(self):
        self._init_memphis()
        from ptah.password import PasswordSchema

        pwdSchema = PasswordSchema.bind(params={})

        data, errors = pwdSchema.extract()
        self.assertEqual(len(errors), 2)
