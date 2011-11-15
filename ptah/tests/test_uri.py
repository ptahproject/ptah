from ptah import config

from base import Base


class TestUri(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestUri, self).tearDown()

    def test_uri_registration(self):
        import ptah

        def resolver1(uri):
            return 'Resolved1'
        def resolver2(uri):
            return 'Resolved2'

        ptah.register_uri_resolver('test1', resolver1)
        ptah.register_uri_resolver('test2', resolver2)
        self._init_ptah()

        self.assertEqual(ptah.resolve('test1:uri'), 'Resolved1')
        self.assertEqual(ptah.resolve('test2:uri'), 'Resolved2')

        self.assertEqual(ptah.resolve(None), None)
        self.assertEqual(ptah.resolve('unknown'), None)
        self.assertEqual(ptah.resolve('unknown:uri'), None)

    def test_uri_registration_decorator(self):
        import ptah

        @ptah.resolver('test1')
        def resolver1(uri):
            return 'Resolved1'

        @ptah.resolver('test2')
        def resolver2(uri):
            return 'Resolved2'

        self._init_ptah()

        self.assertEqual(ptah.resolve('test1:uri'), 'Resolved1')
        self.assertEqual(ptah.resolve('test2:uri'), 'Resolved2')

        self.assertEqual(ptah.resolve(None), None)
        self.assertEqual(ptah.resolve('unknown'), None)
        self.assertEqual(ptah.resolve('unknown:uri'), None)

    def test_uri_registration_conflicts(self):
        import ptah
        ptah.register_uri_resolver('test', None)
        ptah.register_uri_resolver('test', None)

        self.assertRaises(config.ConflictError, self._init_ptah)

    def test_uri_registration_decorator_conflicts(self):
        import ptah

        @ptah.resolver('test1')
        def resolver1(uri): # pragma: no cover
            return 'Resolved1'

        @ptah.resolver('test1')
        def resolver2(uri): # pragma: no cover
            return 'Resolved2'

        self.assertRaises(config.ConflictError, self._init_ptah)

    def test_uri_extract_type(self):
        import ptah

        self.assertEqual(ptah.extract_uri_schema('test:uri'), 'test')
        self.assertEqual(ptah.extract_uri_schema('test'), None)
        self.assertEqual(ptah.extract_uri_schema(None), None)

    def test_uri_uri_generator(self):
        import ptah

        uri = ptah.UriFactory('test')

        u1 = uri()
        u2 = uri()

        self.assertTrue(u1.startswith('test:'))
        self.assertTrue(u2.startswith('test:'))
        self.assertTrue(u1 != u2)
