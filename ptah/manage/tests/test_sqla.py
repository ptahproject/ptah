from pyramid.testing import DummyRequest

from base import Base


class TestSqlaModule(Base):

    def test_sqla_module(self):
        from ptah.manage.manage import CONFIG, PtahManageRoute
        from ptah.manage.sqla import SQLAModule, Table

        request = DummyRequest()

        CONFIG['managers'] = ['*']
        mr = PtahManageRoute(request)
        mod = mr['sqla']
        self.assertIsInstance(mod, SQLAModule)

        self.assertRaises(KeyError, mod.__getitem__, 'psqla-unknown')
        self.assertRaises(KeyError, mod.__getitem__, 'unknown')

        table = mod['psqla-ptah_tokens']
        self.assertIsInstance(table, Table)

    def test_sqla_traverse(self):
        from ptah.manage.sqla import SQLAModule, Table

        request = DummyRequest()

        mod = SQLAModule(None, request)

        table = mod['psqla-ptah_nodes']
        self.assertIsInstance(table, Table)

        self.assertRaises(KeyError, mod.__getitem__, 'unknown')

    def test_sqla_view(self):
        from ptah.manage.sqla import SQLAModule, MainView

        request = DummyRequest()

        mod = SQLAModule(None, request)

        res = MainView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

    def test_table_view(self):
        from ptah.manage.sqla import SQLAModule, TableView

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        res = TableView.__renderer__(table, request)
        self.assertEqual(res.status, '200 OK')

    def test_sqla_table_traverse(self):
        from ptah.manage.sqla import SQLAModule, Record

        from ptah import token
        from ptah.util import CSRFService

        tid = token.service.generate(CSRFService.TOKEN_TYPE, 'test')
        inst = token.service._sql_get.first(token=tid)

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        rec = table[str(inst.id)]

        self.assertIsInstance(rec, Record)
        self.assertEqual(rec.pname, 'id')
        self.assertIsNotNone(rec.pcolumn)
        self.assertIsNotNone(rec.data)

        self.assertRaises(KeyError, table.__getitem__, 'add.html')
        self.assertRaises(KeyError, table.__getitem__, 'unknown')
