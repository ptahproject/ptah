import transaction
from ptah import config
from datetime import timedelta

from base import Base


class TestTokenType(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestTokenType, self).tearDown()

    def test_token(self):
        from ptah import token

        tt = token.TokenType('unique-id', timedelta(minutes=20))
        self._init_ptah()

        t = token.service.generate(tt, 'data')
        transaction.commit()

        self.assertEqual(token.service.get(t), 'data')
        self.assertEqual(token.service.get_bydata(tt, 'data'), t)

        token.service.remove(t)
        self.assertEqual(token.service.get(t), None)

    def test_token_type(self):
        from ptah import token

        token.TokenType('unique-id', timedelta(minutes=20))
        token.TokenType('unique-id', timedelta(minutes=20))

        self.assertRaises(config.ConflictError, self._init_ptah)

    def test_token_remove_expired(self):
        pass
