import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden


class TestAddForm(PtahTestCase):

    def setUp(self):
        global Content, Container
        class Content(ptah.cms.Content):
            __type__ = ptah.cms.Type('content', 'Test Content')
            __uri_factory__ = ptah.UriFactory('cms-content')

        class Container(ptah.cms.Container):
            __type__ = ptah.cms.Type('container', 'Test Container')
            __uri_factory__ = ptah.UriFactory('cms-container')

        self.Content = Content
        self.Container = Container

        super(TestAddForm, self).setUp()

    def test_addform_ctor(self):
        from ptah.cms.forms import AddForm

        container = Container()
        form = AddForm(container, DummyRequest())
        self.assertIs(form.container, container)

    def test_addform_basics(self):
        from ptah.cms.forms import AddForm

        container = Container()

        form = AddForm(container, DummyRequest())
        form.tinfo = Content.__type__

        self.assertIs(form.fields, Content.__type__.fieldset)
        self.assertEqual(form.label, 'Add %s'%Content.__type__.title)
        self.assertEqual(form.description, Content.__type__.description)

    def test_addform_choosename(self):
        from ptah.cms.forms import AddForm

        container = Container()

        form = AddForm(container, DummyRequest())

        name = form.chooseName(title='Test title')
        self.assertEqual(name, 'test-title')

    def test_addform_choosename_existing(self):
        from ptah.cms.forms import AddForm

        container = Container()
        container['test-title'] = Content()

        form = AddForm(container, DummyRequest())

        name = form.chooseName(title='Test title')
        self.assertEqual(name, 'test-title-1')

    def test_addform_choosename_suffix(self):
        from ptah.cms.forms import AddForm

        container = Container()

        form = AddForm(container, DummyRequest())
        form.name_suffix = '.html'

        name = form.chooseName(title='Test title')
        self.assertEqual(name, 'test-title.html')

    def test_addform_update_suffix_from_type(self):
        from ptah.cms.forms import AddForm

        container = Container()

        form = AddForm(container, DummyRequest())

        Content.__type__.name_suffix = '.xml'
        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED

        form.tinfo = Content.__type__
        form.update()

        self.assertEqual(form.name_suffix, '.xml')

        Content.__type__.name_suffix = ''
        Content.__type__.permission = ptah.cms.NOT_ALLOWED

    def test_addform_update_type_check_context(self):
        from ptah.cms.forms import AddForm

        container = Container()

        form = AddForm(container, DummyRequest())

        Content.__type__.permission = ptah.cms.NOT_ALLOWED
        form.tinfo = Content.__type__

        self.assertRaises(HTTPForbidden, form.update)

    def test_addform_name_widgets(self):
        from ptah.cms.forms import AddForm

        form = AddForm(Container(), DummyRequest())

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.update()

        self.assertIsNotNone(form.name_widgets)
        self.assertIn('__name__', form.name_widgets)

    def test_addform_no_name_widgets(self):
        from ptah.cms.forms import AddForm

        form = AddForm(Container(), DummyRequest())

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.name_show = False
        form.update()

        self.assertIsNone(form.name_widgets)

    def test_addform_validate_name(self):
        from ptah.cms.forms import AddForm

        container = Container()
        container['test'] = Content()

        form = AddForm(container, DummyRequest())

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.update()

        errors = []
        form.validate({'__name__': 'test'}, errors)

        self.assertEqual(len(errors), 1)
        self.assertIs(errors[0].field, form.name_widgets['__name__'])
        self.assertEqual(errors[0].msg, 'Name already in use')

        errors = []
        form.validate({'__name__': 'normal-name'}, errors)
        self.assertEqual(len(errors), 0)

    def test_addform_extract_with_errors(self):
        from ptah.cms.forms import AddForm

        form = AddForm(Container(), DummyRequest(
            POST={'__name__': 't/est-content'}))

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.update()

        data, errors = form.extract()

        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].field.name, 'title')
        self.assertEqual(errors[0].msg, 'Required')
        self.assertEqual(errors[1].field.name, '__name__')
        self.assertEqual(errors[1].msg, "Names cannot contain '/'")

    def test_addform_extract_with_errors_no_name(self):
        from ptah.cms.forms import AddForm

        form = AddForm(Container(), DummyRequest(
            POST={'__name__': 't/est-content'}))

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.name_show = False
        form.update()

        data, errors = form.extract()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].field.name, 'title')
        self.assertEqual(errors[0].msg, 'Required')

    def test_addform_extract(self):
        from ptah.cms.forms import AddForm

        form = AddForm(Container(), DummyRequest(
            POST={'title': 'Test Content',
                  '__name__': 'test-content'}))

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.update()

        data, errors = form.extract()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(data), 3)
        self.assertIn('title', data)
        self.assertIn('description', data)
        self.assertIn('__name__', data)

    def test_addform_extract_no_name(self):
        from ptah.cms.forms import AddForm

        form = AddForm(Container(), DummyRequest(
            POST={'title': 'Test Content',
                  '__name__': 'test-content'}))

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.name_show = False
        form.update()

        data, errors = form.extract()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(data), 2)
        self.assertIn('title', data)
        self.assertIn('description', data)

    def test_addform_create_empty_name(self):
        from ptah.cms.forms import AddForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        form = AddForm(Container(), DummyRequest())

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.update()

        content = form.create(**{'title': 'Test Content'})

        self.assertEqual(content.__name__, 'test-content')
        self.assertEqual(content.title, 'Test Content')
        self.assertIsInstance(content, Content)

    def test_addform_create(self):
        from ptah.cms.forms import AddForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        form = AddForm(Container(), DummyRequest())

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.update()

        content = form.create(**{'title': 'Test Content',
                                 '__name__': 'page.html'})

        self.assertEqual(content.__name__, 'page.html')
        self.assertIsInstance(content, Content)

    def test_addform_add(self):
        from ptah.cms.forms import AddForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        container = Container()
        request = DummyRequest(
            POST = {'title': 'Test Content',
                    'form.buttons.add': 'Add'})
        request.root = container
        request.root.__path__ = '/'
        request.root.__root_path__ = '/'

        form = AddForm(container, request)

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__

        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '/test-content/')
        self.assertIn('New content has been created.',
                      ptah.view.render_messages(request))

    def test_addform_add_errors(self):
        from ptah.cms.forms import AddForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        container = Container()
        request = DummyRequest(
            POST = {'form.buttons.add': 'Add'})

        form = AddForm(container, request)
        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__
        form.update()

        self.assertIn('Please fix indicated errors.',
                      ptah.view.render_messages(request))

    def test_addform_cancel(self):
        from ptah.cms.forms import AddForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        container = Container()
        request = DummyRequest(
            POST = {'form.buttons.cancel': 'Cancel'})

        form = AddForm(container, request)

        Content.__type__.permission = ptah.cms.NO_PERMISSION_REQUIRED
        form.tinfo = Content.__type__

        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')


class TestEditForm(PtahTestCase):

    def setUp(self):
        global Content, Container
        class Content(ptah.cms.Content):
            __type__ = ptah.cms.Type('content', 'Test Content')
            __uri_factory__ = ptah.UriFactory('cms-content')

        class Container(ptah.cms.Container):
            __type__ = ptah.cms.Type('container', 'Test Container')
            __uri_factory__ = ptah.UriFactory('cms-container')

        self.Content = Content
        self.Container = Container

        super(TestEditForm, self).setUp()

    def test_editform_basics(self):
        from ptah.cms.forms import EditForm

        content = Content()

        form = EditForm(content, DummyRequest())
        form.update()

        self.assertIs(form.fields, Content.__type__.fieldset)
        self.assertIs(form.tinfo, Content.__type__)
        self.assertEqual(form.label,'Modify content: %s'%Content.__type__.title)

    def test_editform_form_content(self):
        from ptah.cms.forms import EditForm

        content = Content()
        content.title = 'Test content'
        content.description = 'Desc'

        form = EditForm(content, DummyRequest())
        form.update()

        data = form.form_content()

        self.assertEqual(data['title'], 'Test content')
        self.assertEqual(data['description'], 'Desc')

    def test_editform_apply_changes(self):
        from ptah.cms.forms import EditForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        content = Content()
        content.title = 'Test'
        content.description = 'Desc'

        form = EditForm(content, DummyRequest())
        form.update()

        form.apply_changes(**{'title': 'Test2', 'description': 'Desc2'})

        self.assertEqual(content.title, 'Test2')
        self.assertEqual(content.description, 'Desc2')

    def test_editform_save(self):
        from ptah.cms.forms import EditForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        content = Content()
        content.title = 'Test'
        content.description = 'Desc'

        form = EditForm(content, DummyRequest(
            POST = {'title': 'Test2', 'description': 'Desc2',
                    'form.buttons.save': 'Save'}))

        res = form.update()

        self.assertEqual(res.headers['location'], '.')
        self.assertEqual(content.title, 'Test2')
        self.assertEqual(content.description, 'Desc2')
        self.assertIn('Changes have been saved.',
                      ptah.view.render_messages(form.request))

    def test_editform_save_errors(self):
        from ptah.cms.forms import EditForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        content = Content()

        form = EditForm(content, DummyRequest(
            POST = {'form.buttons.save': 'Save'}))

        form.update()

        self.assertIn('Please fix indicated errors.',
                      ptah.view.render_messages(form.request))

    def test_editform_cancel(self):
        from ptah.cms.forms import EditForm
        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        content = Content()

        form = EditForm(content, DummyRequest(
            POST = {'form.buttons.cancel': 'Cancel'}))

        res = form.update()
        self.assertEqual(res.headers['location'], '.')
