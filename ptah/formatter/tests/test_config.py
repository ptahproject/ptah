""" formatter tests """
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationConflictError

from ptah.testing import BaseTestCase


class TestFormatterConfig(BaseTestCase):

    _includes = ['ptah.formatter']

    def test_formatter_registration(self):
        def simple(request, v):
            return 'simple-%s'%v

        self.config.add_formatter('simple', simple)

        request = self.make_request()
        self.assertEqual(request.fmt.simple('test'), 'simple-test')
        self.assertIs(request.fmt.simple.callable, simple)

    def test_formatter_cache(self):
        def simple(request, v):
            return 'simple-%s'%v

        self.config.add_formatter('simple', simple)

        simple = self.request.fmt['simple']
        self.assertIs(simple, self.request.fmt['simple'])
        self.assertIs(self.request.fmt['simple'], self.request.fmt.simple)

        request = self.make_request()
        self.assertIsNot(simple, request.fmt.simple)

    def test_formatter_unknown(self):
        request = self.make_request()
        self.assertRaises(
            AttributeError, request.fmt.__getattr__, 'simple')
        self.assertRaises(
            KeyError, request.fmt.__getitem__, 'simple')

    def test_formatter_registration_duplicate(self):
        def simple1(v):
            """ """

        def simple2(v):
            """ """

        config = Configurator()
        config.include('ptah.formatter')

        config.add_formatter('test', simple1)
        config.add_formatter('test', simple2)

        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_formatter_introspector(self):
        def simple(v):
            """ doc """

        self.config.add_formatter('simple', simple)

        from ptah.formatter.config import ID_FORMATTER

        discr = (ID_FORMATTER, 'simple')
        intr = self.config.introspector.get(ID_FORMATTER, discr)

        self.assertIsNotNone(intr)
        self.assertEqual(intr['name'], 'simple')
        self.assertEqual(intr['description'], ' doc ')
        self.assertEqual(intr['callable'], simple)
