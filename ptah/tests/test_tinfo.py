import transaction
import sqlalchemy as sqla
from pyramid.httpexceptions import HTTPForbidden
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError

from ptah import config, form
from ptah.testing import PtahTestCase, TestCase


class TestTypeInfo(PtahTestCase):

    _init_auth = True
    _init_ptah = False

    def tearDown(self):
        super(TestTypeInfo, self).tearDown()

        from ptah import tinfo
        t = []
        for name, h in tinfo.phase_data:
            if name !='test':
                t.append((name, h))
        tinfo.phase_data[:] = t

    def test_tinfo(self):
        import ptah

        @ptah.type('mycontent', 'MyContent')
        class Mycontent(object):
            pass

        self.init_ptah()

        all_types = ptah.get_types()

        self.assertTrue('type:mycontent' in all_types)

        tinfo = ptah.get_type('type:mycontent')

        self.assertEqual(tinfo.__uri__, 'type:mycontent')
        self.assertEqual(tinfo.name, 'mycontent')
        self.assertEqual(tinfo.title, 'MyContent')
        self.assertIs(tinfo.cls, Mycontent)
        self.assertIs(Mycontent.__type__, tinfo)

    def test_tinfo_title(self):
        import ptah

        @ptah.type('mycontent')
        class MyContent(object):
            pass

        self.assertEqual(MyContent.__type__.title, 'Mycontent')

        @ptah.type('mycontent', 'MyContent')
        class MyContent(object):
            pass

        self.assertEqual(MyContent.__type__.title, 'MyContent')

    def test_tinfo_checks(self):
        import ptah

        @ptah.type('mycontent', 'Content', permission=None)
        class MyContent(object):
            pass
        @ptah.type('mycontainer', 'Container')
        class MyContainer(object):
            pass
        self.init_ptah()

        content = MyContent()
        container = MyContainer()

        #
        self.assertTrue(MyContent.__type__.is_allowed(container))
        self.assertEqual(MyContent.__type__.check_context(container), None)

        # permission
        MyContent.__type__.permission = 'Protected'
        self.assertFalse(MyContent.__type__.is_allowed(container))
        self.assertRaises(
            HTTPForbidden, MyContent.__type__.check_context, container)

    def test_tinfo_list(self):
        import ptah

        @ptah.type('mycontent', 'Content', permission=None)
        class MyContent(object):
            pass
        @ptah.type('mycontainer', 'Container')
        class MyContainer(object):
            pass
        self.init_ptah()

        content = MyContent()
        container = MyContainer()

        self.assertEqual(MyContent.__type__.list_types(content), [])
        self.assertEqual(MyContent.__type__.list_types(container), ())

        MyContent.__type__.global_allow = True
        self.assertEqual(MyContainer.__type__.list_types(container),
                         [MyContent.__type__])

        MyContent.__type__.global_allow = False
        self.assertEqual(MyContainer.__type__.list_types(container), [])

        MyContent.__type__.global_allow = True
        MyContent.__type__.permission = 'Protected'
        self.assertEqual(MyContainer.__type__.list_types(container), [])

    def test_tinfo_list_filtered(self):
        import ptah

        @ptah.type('mycontent', 'Content', permission=None)
        class MyContent(object):
            pass

        @ptah.type('mycontainer', 'Container', filter_content_types=True)
        class MyContainer(object):
            pass
        self.init_ptah()

        container = MyContainer()
        self.assertEqual(MyContainer.__type__.list_types(container), [])

        MyContainer.__type__.allowed_content_types = ('mycontent',)
        self.assertEqual(MyContainer.__type__.list_types(container),
                         [MyContent.__type__])

    def test_tinfo_list_filtered_callable(self):
        import ptah

        @ptah.type('mycontent', 'Content', permission=None)
        class MyContent(object):
            pass
        @ptah.type('mycontainer', 'Container', filter_content_types=True)
        class MyContainer(object):
            pass

        self.init_ptah()

        container = MyContainer()
        self.assertEqual(MyContainer.__type__.list_types(container), [])

        def filter(content):
            return ('mycontent',)

        MyContainer.__type__.allowed_content_types = filter
        self.assertEqual(MyContainer.__type__.list_types(container),
                         [MyContent.__type__])

    def test_tinfo_conflicts(self):
        import ptah

        @ptah.type('mycontent2', 'MyContent')
        class MyContent(object):
            pass
        @ptah.type('mycontent2', 'MyContent')
        class MyContent2(object):
            pass

        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_tinfo_create(self):
        import ptah

        @ptah.type('mycontent', 'MyContent')
        class MyContent(object):

            def __init__(self, title=''):
                self.title = title

        self.init_ptah()

        all_types = ptah.get_types()

        content = all_types['type:mycontent'].create(title='Test content')

        self.assertTrue(isinstance(content, MyContent))
        self.assertEqual(content.title, 'Test content')

    def test_tinfo_fieldset(self):
        import ptah

        MySchema = ptah.form.Fieldset(form.TextField('test'))

        @ptah.type('mycontent2', 'MyContent', fieldset=MySchema)
        class MyContent(object):
            pass

        tinfo = MyContent.__type__
        self.assertIs(tinfo.fieldset, MySchema)

    def test_tinfo_type_resolver(self):
        import ptah

        @ptah.type('mycontent2', 'MyContent')
        class MyContent(object):
            pass

        self.init_ptah()

        tinfo_uri = MyContent.__type__.__uri__

        self.assertEqual(tinfo_uri, 'type:mycontent2')
        self.assertIs(ptah.resolve(tinfo_uri), MyContent.__type__)

    def test_add_method(self):
        import ptah

        @ptah.type('mycontent2', 'MyContent')
        class MyContent(object):
            pass

        self.init_ptah()

        tinfo = MyContent.__type__

        err=None
        try:
            tinfo.add(None, MyContent())
        except Exception as e:
            err=e

        self.assertIsNotNone(err)

        added = []
        def add_content(item):
            added.append(item)

        tinfo.add_method = add_content

        item = MyContent()
        tinfo.add(item)
        self.assertIn(item, added)

    def test_phase2_err(self):
        from ptah.tinfo import phase2

        @phase2('test')
        def t(): pass

        err = None
        try:
            @phase2('test')
            def t1(): pass
        except Exception as e:
            err = e

        self.assertIsNotNone(err)


class TestSqlTypeInfo(PtahTestCase):

    _init_auth = True
    _init_ptah = False

    def tearDown(self):
        super(TestSqlTypeInfo, self).tearDown()

        from ptah import tinfo
        t = []
        for name, h in tinfo.phase_data:
            if name !='test':
                t.append((name, h))
        tinfo.phase_data[:] = t

    def test_tinfo(self):
        import ptah
        from ptah import tinfo
        import sqlalchemy as sqla

        @ptah.type('mycontent', 'MyContent')
        class MyContentSql(ptah.get_base()):

            __tablename__ = 'tinfo_sql_test'

            id = sqla.Column('id', sqla.Integer, primary_key=True)

        self.init_ptah()

        ti = ptah.get_type('type:mycontent')
        self.assertIs(ti.add_method, tinfo.sqla_add_method)

    def test_custom_fieldset(self):
        import ptah
        from ptah import tinfo
        import sqlalchemy as sqla

        @ptah.type('mycontent', 'MyContent')
        class MyContentSql(ptah.get_base()):

            __tablename__ = 'tinfo_sql_test2'

            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)

        self.init_ptah()

        ti = ptah.get_type('type:mycontent')
        self.assertIn('test', ti.fieldset)

    def test_custom_fieldset_fieldNames(self):
        import ptah
        from ptah import tinfo
        import sqlalchemy as sqla

        @ptah.type('mycontent', 'MyContent', fieldNames=['test'])
        class MyContentSql(ptah.get_base()):

            __tablename__ = 'tinfo_sql_test21'

            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)
            test1 = sqla.Column(sqla.Unicode)

        self.init_ptah()

        ti = ptah.get_type('type:mycontent')
        self.assertIn('test', ti.fieldset)
        self.assertNotIn('test1', ti.fieldset)

    def test_custom_fieldset_namesFilter(self):
        import ptah
        from ptah import tinfo
        import sqlalchemy as sqla

        def filter(n, names):
            return n != 'test'

        @ptah.type('mycontent', 'MyContent', namesFilter=filter)
        class MyContentSql(ptah.get_base()):

            __tablename__ = 'tinfo_sql_test22'

            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)
            test1 = sqla.Column(sqla.Unicode)

        self.init_ptah()

        ti = ptah.get_type('type:mycontent')
        self.assertIn('test1', ti.fieldset)
        self.assertNotIn('test', ti.fieldset)

    def test_sqla_add_method(self):
        import ptah
        from ptah import tinfo
        import sqlalchemy as sqla

        @ptah.type('mycontent', 'MyContent')
        class MyContentSql(ptah.get_base()):

            __tablename__ = 'tinfo_sql_test3'

            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)

        self.init_ptah()

        ti = ptah.get_type('type:mycontent')

        item = ti.add(MyContentSql(test='title'))
        sa = ptah.get_session()
        self.assertIn(item, sa)

    def test_uri_prop(self):
        import ptah
        import sqlalchemy as sqla

        @ptah.type('mycontent', 'MyContent')
        class MyContentSql(ptah.get_base()):

            __tablename__ = 'tinfo_sql_test4'
            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)

        self.init_ptah()

        self.assertTrue(hasattr(MyContentSql, '__uri__'))

        self.assertEqual(MyContentSql.__uri__.cname, 'id')
        self.assertEqual(MyContentSql.__uri__.prefix, 'mycontent')

    def test_uri_prop_exist(self):
        import ptah
        import sqlalchemy as sqla

        @ptah.type('mycontent', 'MyContent')
        class MyContentSql(ptah.get_base()):

            __uri__ = 'test'
            __tablename__ = 'tinfo_sql_test5'
            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)

        self.init_ptah()
        self.assertTrue(MyContentSql.__uri__, 'test')

    def test_uri_resolver_exists(self):
        import ptah
        import sqlalchemy as sqla

        def resolver(uri):
            """"""
        ptah.resolver.register('mycontent', resolver)

        @ptah.type('mycontent', 'MyContent')
        class MyContentSql(ptah.get_base()):
            __tablename__ = 'tinfo_sql_test6'

            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)

        self.assertRaises(ConfigurationError, self.init_ptah)

    def test_uri_resolver(self):
        import ptah
        import sqlalchemy as sqla

        @ptah.type('mycontent', 'MyContent')
        class MyContentSql(ptah.get_base()):
            __tablename__ = 'tinfo_sql_test7'

            id = sqla.Column(sqla.Integer, primary_key=True)
            test = sqla.Column(sqla.Unicode)

        self.init_ptah()

        id = None
        uri = None

        with ptah.sa_session() as sa:
            item = MyContentSql(test='title')
            sa.add(item)
            sa.flush()

            id = item.id
            uri = item.__uri__

        self.assertEqual(uri, 'mycontent:%s'%id)

        item = ptah.resolve(uri)
        self.assertTrue(item.id == id)


class TestUriProperty(TestCase):

    def test_uri_property(self):
        from ptah.tinfo import UriProperty

        class Test(object):

            __uri__ = UriProperty('test-uri', 'id')

        self.assertTrue(isinstance(Test.__uri__, UriProperty))

        item = Test()
        item.id = 10

        self.assertEqual(item.__uri__, 'test-uri:10')
