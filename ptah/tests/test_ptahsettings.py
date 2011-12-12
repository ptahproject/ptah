import ptah
from ptah import config
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

from ptah.testing import PtahTestCase


class TestSecurityInit(PtahTestCase):

    _init_ptah = False
    _init_sqla = False

    def test_ptahinit_mail(self):
        self._settings = {'mail.host': 'smtp.ptahproject.org',
                          'mail.from_name': 'Ptah admin',
                          'mail.from_address': 'admin@ptahproject.org'}
        self.init_ptah()

        MAIL = ptah.get_settings(ptah.CFG_ID_MAIL, self.registry)

        self.assertIsNotNone(MAIL['Mailer'])
        self.assertEqual(MAIL['full_from_address'],
                         'Ptah admin <admin@ptahproject.org>')
        self.assertEqual(MAIL['Mailer'].mailer.hostname, 'smtp.ptahproject.org')

    def test_ptahinit_sqla(self):
        self._settings = {'sqla.url': 'sqlite://'}
        self.init_ptah()

        import sqlahelper

        engine = sqlahelper.get_engine()
        self.assertIsNotNone(engine)
