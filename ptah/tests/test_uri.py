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

        self.assertEqual(ptah.resolve('test1:uuid'), 'Resolved1')
        self.assertEqual(ptah.resolve('test2:uuid'), 'Resolved2')

        self.assertEqual(ptah.resolve(None), None)
        self.assertEqual(ptah.resolve('unknown'), None)
        self.assertEqual(ptah.resolve('unknown:uuid'), None)

    def test_uri_registration_conflicts(self):
        import ptah
        ptah.registerResolver('test', None)
        ptah.registerResolver('test', None)

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_uri_extract_type(self):
        import ptah

        self.assertEqual(ptah.extractUriType('test:uuid'), 'test')
        self.assertEqual(ptah.extractUriType('test'), None)
        self.assertEqual(ptah.extractUriType(None), None)

    def test_uri_uuid_generator(self):
        import ptah

        uuid = ptah.UUIDGenerator('test')

        u1 = uuid()
        u2 = uuid()

        self.assertTrue(u1.startswith('test:'))
        self.assertTrue(u2.startswith('test:'))
        self.assertTrue(u1 != u2)
