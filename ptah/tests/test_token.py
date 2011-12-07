import transaction
from datetime import timedelta
from pyramid.exceptions import ConfigurationConflictError

from ptah.testing import PtahTestCase


class TestTokenType(PtahTestCase):

    _init_ptah = False

    def test_token(self):
        from ptah import token

        tt = token.TokenType('unique-id', timedelta(minutes=20))
        self.init_ptah()

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

        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_token_remove_expired(self):
        pass
