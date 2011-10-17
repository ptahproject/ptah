import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestSqlaModule(Base):

    def test_sqla_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.sqla import SQLAModule, Table

        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['sqla']

        self.assertIsInstance(mod, SQLAModule)

        self.assertRaises(KeyError, mod.__getitem__, 'psqla-unknown')
        self.assertRaises(KeyError, mod.__getitem__, 'unknown')

        table = mod['psqla-ptah_tokens']
        self.assertIsInstance(table, Table)

    def test_sqla_view(self):
        from ptah.manage.sqla import SQLAModule, MainView

        request = DummyRequest()

        mod = SQLAModule(None, request)

        res = MainView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

    def test_table_view(self):
        from ptah.manage.sqla import SQLAModule, Table, TableView

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        res = TableView.__renderer__(table, request)
        self.assertEqual(res.status, '200 OK')
