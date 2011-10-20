import ptah
from ptah import config
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

from base import Base


class TestSecurityInit(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestSecurityInit, self).tearDown()

    def test_srvinit_nopolicy(self):
        from ptah.settings import SECURITY
        self._init_ptah({'auth.policy': 'no-policy'})

        auth = config.registry.queryUtility(IAuthenticationPolicy)
        self.assertIsNone(auth)

    def test_srvinit_authtkt(self):
        self._init_ptah({'auth.policy': 'auth_tkt',
                         'auth.secret': 'test-secret'})

        auth = config.registry.queryUtility(IAuthenticationPolicy)
        self.assertIsInstance(auth, AuthTktAuthenticationPolicy)
        self.assertEqual(auth.cookie.secret, 'test-secret')

    def test_srvinit_mail(self):
        self._init_ptah({'mail.host': 'smtp.ptahproject.org',
                         'mail.from_name': 'Ptah admin',
                         'mail.from_address': 'admin@ptahproject.org'})

        from ptah import MAIL

        self.assertIsNotNone(MAIL.Mailer)
        self.assertEqual(MAIL.full_from_address,
                         'Ptah admin <admin@ptahproject.org>')
        self.assertEqual(MAIL.Mailer.mailer.hostname, 'smtp.ptahproject.org')
