import ptah
from ptah import config
from pyramid.interfaces import ISessionFactory
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

from ptah.testing import PtahTestCase


class TestSecurityInit(PtahTestCase):

    _init_ptah = False

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

    def test_ptahinit_nosession(self):
        self._settings = {'session.enabled': 'false'}
        self.init_ptah()

        session = self.registry.queryUtility(ISessionFactory)
        self.assertIsNone(session)

    def test_ptahinit_session(self):
        self._settings = {'session.enabled': 'true',
                          'session.secret': '12345',
                          'sesison.data_dir': './data_dir',
                          'sesison.lock_dir': './lock_dir'}
        self.init_ptah()

        session = self.registry.queryUtility(ISessionFactory)
        self.assertIsNotNone(session)
