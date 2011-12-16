import transaction
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

import ptah
from ptah.testing import PtahTestCase


class TestLoadApi(PtahTestCase):
    """ fixme: redesign tests to use custom resolver """

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

        super(TestLoadApi, self).setUp()

    def test_loadapi_load(self):
        content = Content(title='Content')
        uri = content.__uri__

        ptah.get_session().add(content)
        transaction.commit()

        content = ptah.cms.load(uri)
        self.assertEqual(content.__uri__, uri)

    def test_loadapi_load_notfound(self):
        self.assertRaises(HTTPNotFound, ptah.cms.load, 'unknown')

    def test_loadapi_load_with_parents(self):
        content = Content(title='Content')
        container = Container(__name__='container', __path__='/container/')

        c_uri = content.__uri__
        co_uri = container.__uri__
        Session = ptah.get_session()
        Session.add(container)
        Session.add(content)
        transaction.commit()

        container = ptah.resolve(co_uri)
        container['content'] = ptah.resolve(c_uri)
        transaction.commit()

        content = ptah.cms.load(c_uri)
        self.assertEqual(content.__parent__.__uri__, co_uri)

    def test_loadapi_load_permission(self):
        import ptah

        allow = False
        def check_permission(permission, content, r=None, t=True):
            if not allow:
                return False

            return True

        # monkey patch
        orig_check_permission = ptah.check_permission
        ptah.check_permission = check_permission

        c = Content(title='Content')
        uri = c.__uri__
        Session = ptah.get_session()
        Session.add(c)
        transaction.commit()

        self.assertRaises(HTTPForbidden, ptah.cms.load, uri, 'View')

        allow = True
        c = ptah.cms.load(uri, 'View')
        self.assertEqual(c.__uri__, uri)

        # remove monkey patch
        ptah.check_permission = orig_check_permission
