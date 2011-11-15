import transaction
from zope import interface
import ptah, ptah.cms
from ptah import config
from pyramid.testing import DummyRequest

from base import Base


class RestBase(Base):

    _allow = True

    def _check_perm(self, perm, content, request=None, throw=False):
        return self._allow

    def _setup_ptah(self):
        pass

    def _make_app(self):
        global ApplicationRoot
        class ApplicationRoot(ptah.cms.ApplicationRoot):
            __type__ = ptah.cms.Type('app')

        ApplicationRoot.__type__.cls = ApplicationRoot

        return ApplicationRoot

    def setUp(self):
        super(RestBase, self).setUp()

        self.orig_check_permission = ptah.check_permission
        ptah.check_permission = self._check_perm
        ptah.cms.ApplicationFactory._sql_get_root.reset()

    def tearDown(self):
        ptah.check_permission = self.orig_check_permission

        config.cleanup_system(self.__class__.__module__)
        super(RestBase, self).tearDown()


class TestRestApi(RestBase):

    def test_rest_srv(self):
        import ptah.rest
        self._init_ptah()

        services = config.get_cfg_storage(ptah.rest.REST_ID)

        self.assertIn('cms', services)

        srv = services['cms']
        self.assertEqual(srv.title, 'Ptah CMS API')
        self.assertEqual(srv.actions.keys(),
                         ['content', 'applications', 'apidoc', 'types'])

    def test_rest_applications(self):
        from ptah.cms.rest import cmsApplications

        ApplicationRoot = self._make_app()

        self._init_ptah()

        request = self._makeRequest()

        info = cmsApplications(request)
        self.assertEqual(info, [])

        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '/test', 'root', 'Root App', config=self.p_config)

        info = cmsApplications(request)
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0]['__name__'], 'root')
        self.assertEqual(info[0]['__mount__'], 'test')
        self.assertEqual(info[0]['__link__'],
                         'http://localhost:8080/content:%s/%s/'%(
                info[0]['__mount__'], info[0]['__uri__']))

        ptah.cms.ApplicationFactory(
            ApplicationRoot, '/test2', 'root2', 'Root App',config=self.p_config)
        self.assertEqual(len(cmsApplications(request)), 2)

        self._allow = False
        self.assertEqual(len(cmsApplications(request)), 0)

    def test_rest_applications_default(self):
        from ptah.cms.rest import cmsApplications

        ApplicationRoot = self._make_app()

        self._init_ptah()

        request = self._makeRequest()

        info = cmsApplications(request)
        self.assertEqual(info, [])

        ptah.cms.ApplicationFactory(
            ApplicationRoot, '/', 'root', 'Root App', config=self.p_config)

        info = cmsApplications(request)
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0]['__name__'], 'root')
        self.assertEqual(info[0]['__mount__'], '')
        self.assertEqual(
            info[0]['__link__'],
            'http://localhost:8080/content/%s/'%(info[0]['__uri__'],))

    def test_rest_types(self):
        from ptah.cms.rest import cmsTypes

        self._make_app()
        self._init_ptah()

        request = self._makeRequest()
        info = cmsTypes(request)

        self.assertEqual(info[0]['name'], 'app')
        self.assertEqual(info[0]['__uri__'], 'cms-type:app')
        self.assertEqual(len(info[0]['fieldset']), 2)
        self.assertEqual(info[0]['fieldset'][0]['name'], 'title')
        self.assertEqual(info[0]['fieldset'][1]['name'], 'description')

    def test_rest_content(self):
        from ptah.cms.rest import cmsContent
        ApplicationRoot = self._make_app()
        self._init_ptah()

        request = DummyRequest(
            subpath=('content:root',), environ=self._makeEnviron())
        self.assertRaises(ptah.cms.NotFound, cmsContent, request, 'root')

        request = DummyRequest(
            subpath=('content:test',), environ=self._makeEnviron())
        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '/test', 'root', 'Root App', config=self.p_config)
        root = factory(request)
        root.__uri__ = 'cms-app:test'
        transaction.commit()

        self._allow = False
        self.assertRaises(ptah.cms.Forbidden, cmsContent, request, 'test')

        self._allow = True

        root = factory(request)

        info = cmsContent(request, 'test')
        self.assertEqual(info['__uri__'], root.__uri__)

        self.assertRaises(ptah.cms.NotFound,
                          cmsContent, request, 'test', action='unknown')

        info = cmsContent(request, 'test', root.__uri__)
        self.assertEqual(info['__uri__'], root.__uri__)

    def test_rest_content_default(self):
        from ptah.cms.rest import cmsContent
        ApplicationRoot = self._make_app()
        self._init_ptah()

        request = DummyRequest(subpath=('content',),environ=self._makeEnviron())

        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '/', 'root', 'Root App', config=self.p_config)
        root = factory(request)
        root.__uri__ = 'cms-app:test'
        transaction.commit()

        self._allow = False
        self.assertRaises(ptah.cms.Forbidden, cmsContent, request)

        self._allow = True

        root = factory(request)

        info = cmsContent(request)
        self.assertEqual(info['__uri__'], root.__uri__)

        self.assertRaises(ptah.cms.NotFound,
                          cmsContent, request, action='unknown')

        info = cmsContent(request, root.__uri__)
        self.assertEqual(info['__uri__'], root.__uri__)


class Content(ptah.cms.Content):

    __type__ = ptah.cms.Type('content', 'Test Content')
    __uri_factory__ = ptah.UriFactory('cms-content')


class Container(ptah.cms.Container):

    __type__ = ptah.cms.Type('container', 'Test Container')
    __uri_factory__ = ptah.UriFactory('cms-container')


class TestCMSRestAction(RestBase):

    def test_rest_cms_action(self):
        from ptah.cms.rest import IRestAction, IRestActionClassifier

        @ptah.cms.restaction('my-update', Content, ptah.cms.View)
        def update(content, request, *args):
            """ doc string """

        self._init_ptah()

        adapters = self.p_config.registry.adapters

        action = adapters.lookup(
            (IRestActionClassifier, interface.implementedBy(Content)),
            IRestAction, name='my-update')

        self.assertEqual(action.callable, update)
        self.assertEqual(action.name, 'my-update')
        self.assertEqual(action.description, update.__doc__)
        self.assertEqual(action.permission, ptah.cms.View)

    def test_rest_cms_action_conflicts(self):
        @ptah.cms.restaction('my-update', Content, ptah.cms.View)
        def update1(content, request, *args):
            """ doc string """

        @ptah.cms.restaction('my-update', Content, ptah.cms.View)
        def update2(content, request, *args):
            """ doc string """

        self.assertRaises(config.ConflictError, self._init_ptah)

    def test_rest_cms_node_info(self):
        from ptah.cms import rest
        self._init_ptah()

        content = Content()
        request = self._makeRequest()
        info = rest.nodeInfo(content, request)

        self.assertEqual(info['__uri__'], content.__uri__)
        self.assertEqual(info['__link__'],
                         '%s%s/'%(request.application_url, content.__uri__))

    def test_rest_cms_apidoc(self):
        from ptah.cms import rest
        self._init_ptah()

        content = Content()
        request = self._makeRequest()
        request.registry = self.p_config.registry
        info = rest.apidocAction(content, request)
        self.assertEqual(len(info), 5)
        self.assertEqual(info[0]['name'], 'info')

        self._allow = False
        info = rest.apidocAction(content, request)
        self.assertEqual(len(info), 0)

    def test_rest_cms_container_info(self):
        from ptah.cms import rest
        self._init_ptah()

        container = Container()
        container['content'] = Content()

        request = self._makeRequest()
        info = rest.containerNodeInfo(container, request)

        self.assertEqual(info['__uri__'], container.__uri__)
        self.assertEqual(info['__link__'],
                         '%s%s/'%(request.application_url, container.__uri__))
        self.assertEqual(len(info['__contents__']), 1)
        self.assertEqual(info['__contents__'][0]['__uri__'],
                         container['content'].__uri__)

    def test_rest_cms_delete(self):
        from ptah.cms import rest
        self._init_ptah()

        container = Container()
        container['content'] = Content()

        request = self._makeRequest()
        rest.deleteAction(container['content'], request)
        self.assertEqual(container.keys(), [])

    def test_rest_cms_update(self):
        from ptah.cms import rest
        self._init_ptah()

        content = Content(title='Test')

        request = DummyRequest(params = {'title':''})
        info = rest.updateAction(content, request)
        self.assertEqual(info['errors']['title'], 'Required')

        request = DummyRequest(params = {'title':'New title'})

        info = rest.updateAction(content, request)
        self.assertEqual(
            info['__link__'],
            '%s%s/'%(request.application_url, content.__uri__))
        self.assertEqual(content.title, 'New title')

    def test_rest_cms_create(self):
        from ptah.cms import rest
        self._init_ptah()

        all_types = ptah.cms.get_types()

        all_types[Content.__type__.__uri__] = Content.__type__

        container = Container()

        request = DummyRequest(
            params = {'tinfo': Content.__type__.__uri__, 'name': 'content'},
            post = {'title':''})
        info = rest.createContentAction(container, request)
        self.assertEqual(info['errors']['title'], 'Required')

        request = DummyRequest(
            params = {'tinfo': Content.__type__.__uri__, 'name': 'content'},
            post = {'title':'New title'})

        rest.createContentAction(container, request)
        self.assertEqual(container.keys(), ['content'])
        self.assertEqual(container['content'].title, 'New title')
