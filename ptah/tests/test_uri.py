import unittest
from memphis import config

from base import Base


class TestUri(Base):

    def test_uri_registration(self):
        import ptah

        def resolver1(uri):
            return 'Resolved1'
        def resolver2(uri):
            return 'Resolved2'

        ptah.registerResolver('test1', resolver1)
        ptah.registerResolver('test2', resolver2)

        self.assertEqual(ptah.resolve('test1:uri'), 'Resolved1')
        self.assertEqual(ptah.resolve('test2:uri'), 'Resolved2')

        self.assertEqual(ptah.resolve(None), None)
        self.assertEqual(ptah.resolve('unknown'), None)
        self.assertEqual(ptah.resolve('unknown:uri'), None)

    def test_uri_registration_conflicts(self):
        import ptah
        ptah.registerResolver('test', None)
        ptah.registerResolver('test', None)

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_uri_extract_type(self):
        import ptah

        self.assertEqual(ptah.extractUriSchema('test:uri'), 'test')
        self.assertEqual(ptah.extractUriSchema('test'), None)
        self.assertEqual(ptah.extractUriSchema(None), None)

    def test_uri_uri_generator(self):
        import ptah

        uri = ptah.UriGenerator('test')

        u1 = uri()
        u2 = uri()

        self.assertTrue(u1.startswith('test:'))
        self.assertTrue(u2.startswith('test:'))
        self.assertTrue(u1 != u2)
