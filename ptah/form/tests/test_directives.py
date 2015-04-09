import mock
import ptah.form
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationConflictError

from ptah.testing import BaseTestCase


class TestFieldset(BaseTestCase):

    _includes = ['ptah.form']

    @mock.patch('ptah.form.directives.venusian')
    def test_declarative(self, m_venusian):

        @ptah.form.field('my-field')
        class MyField(ptah.form.Field):
            pass

        wrp, cb = m_venusian.attach.call_args[0]

        self.assertIs(wrp, MyField)

        m_venusian.config.with_package.return_value = self.config
        cb(m_venusian, 'my-field', MyField)

        self.assertIs(ptah.form.get_field_factory(self.request, 'my-field'), MyField)

    def test_imperative(self):
        class MyField(ptah.form.Field):
            """ """

        self.config.provide_form_field('my-field', MyField)
        self.assertIs(ptah.form.get_field_factory(self.request, 'my-field'), MyField)

    def test_conflict(self):

        class MyField(ptah.form.Field):
            pass

        class MyField2(ptah.form.Field):
            pass

        config = Configurator()
        config.include('ptah.form')
        config.provide_form_field('my-field', MyField)
        config.provide_form_field('my-field', MyField2)

        self.assertRaises(ConfigurationConflictError, config.commit)

    @mock.patch('ptah.form.directives.venusian')
    def test_preview(self, m_venusian):

        class MyField(ptah.form.Field):
            pass

        @ptah.form.fieldpreview(MyField)
        def preview(request):
            """ """

        wrp, cb = m_venusian.attach.call_args[0]

        self.assertIs(wrp, preview)

        m_venusian.config.with_package.return_value = self.config
        cb(m_venusian, MyField, preview)

        from ptah.form.directives import ID_PREVIEW
        previews = self.registry[ID_PREVIEW]

        self.assertIn(MyField, previews)
        self.assertIs(previews[MyField], preview)
        self.assertIs(ptah.form.get_field_preview(self.request, MyField), preview)
