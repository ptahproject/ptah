import ptah
from ptah import config
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

from ptah.testing import PtahTestCase


class TestSecurityInit(PtahTestCase):

    _init_ptah = False
    _init_sqla = False

    def test_ptahinit_sqla(self):
        self._settings = {'sqla.url': 'sqlite://'}
        self.init_ptah()

        import sqlahelper

        engine = sqlahelper.get_engine()
        self.assertIsNotNone(engine)
