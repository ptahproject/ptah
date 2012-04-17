import transaction
import sqlalchemy as sqla
from pyramid.httpexceptions import HTTPForbidden
from pyramid.exceptions import ConfigurationConflictError

from ptah import config, form
from ptah.testing import PtahTestCase


class TestTypeInfo(PtahTestCase):

    _init_auth = True
    _init_ptah = False

    def test_tinfo(self):
        import ptah

        global MyContent
        class MyContent(object):

            __type__ = ptah.Type('mycontent', 'MyContent')

        self.init_ptah()

        all_types = ptah.get_types()

        self.assertTrue('type:mycontent' in all_types)

        tinfo = ptah.get_type('type:mycontent')

        self.assertEqual(tinfo.__uri__, 'type:mycontent')
        self.assertEqual(tinfo.name, 'mycontent')
        self.assertEqual(tinfo.title, 'MyContent')
        self.assertEqual(tinfo.cls, MyContent)

    def test_tinfo_title(self):
        import ptah

        class MyContent(object):
            __type__ = ptah.Type('mycontent')

        self.assertEqual(MyContent.__type__.title, 'Mycontent')

        class MyContent(object):
            __type__ = ptah.Type('mycontent', 'MyContent')

        self.assertEqual(MyContent.__type__.title, 'MyContent')

    def test_tinfo_checks(self):
        import ptah

        global MyContent, MyContainer
        class MyContent(object):
            __type__ = ptah.Type('mycontent', 'Content', permission=None)
        class MyContainer(object):
            __type__ = ptah.Type('mycontainer', 'Container')
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

        global MyContent, MyContainer
        class MyContent(object):
            __type__ = ptah.Type('mycontent', 'Content', permission=None)
        class MyContainer(object):
            __type__ = ptah.Type('mycontainer', 'Container')
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

        global MyContent, MyContainer
        class MyContent(object):
            __type__ = ptah.Type('mycontent', 'Content', permission=None)
        class MyContainer(object):
            __type__ = ptah.Type('mycontainer', 'Container',
                                 filter_content_types=True)
        self.init_ptah()

        container = MyContainer()
        self.assertEqual(MyContainer.__type__.list_types(container), [])

        MyContainer.__type__.allowed_content_types = ('mycontent',)
        self.assertEqual(MyContainer.__type__.list_types(container),
                         [MyContent.__type__])

    def test_tinfo_list_filtered_callable(self):
        import ptah

        global MyContent, MyContainer
        class MyContent(object):
            __type__ = ptah.Type('mycontent', 'Content', permission=None)
        class MyContainer(object):
            __type__ = ptah.Type('mycontainer', 'Container',
                                 filter_content_types=True)

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

        global MyContent
        class MyContent(object):
            __type__ = ptah.Type('mycontent2', 'MyContent')
        class MyContent2(object):
            __type__ = ptah.Type('mycontent2', 'MyContent')

        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_tinfo_create(self):
        import ptah

        global MyContent
        class MyContent(object):
            __type__ = ptah.Type('mycontent', 'MyContent')

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

        class MyContent(object):
            __type__ = ptah.Type('mycontent2', 'MyContent',
                                 fieldset=MySchema)

        tinfo = MyContent.__type__
        self.assertIs(tinfo.fieldset, MySchema)

    def test_tinfo_type_resolver(self):
        import ptah

        global MyContent
        class MyContent(object):
            __type__ = ptah.Type('mycontent2', 'MyContent')

        self.init_ptah()

        tinfo_uri = MyContent.__type__.__uri__

        self.assertEqual(tinfo_uri, 'type:mycontent2')
        self.assertIs(ptah.resolve(tinfo_uri), MyContent.__type__)
