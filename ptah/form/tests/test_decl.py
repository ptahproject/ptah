from ptah import form, config
from ptah.testing import PtahTestCase
from pyramid.exceptions import ConfigurationConflictError


class TestFieldset(PtahTestCase):

    _init_ptah = False

    def test_decl(self):
        @form.field('my-field')
        class MyField(form.Field):
            pass

        self.init_ptah()
        self.assertIs(form.get_field_factory('my-field'), MyField)

    def test_decl_register(self):

        class MyField(form.Field):
            """ """

        form.field.register('my-field', MyField)

        self.init_ptah()
        self.assertIs(form.get_field_factory('my-field'), MyField)

    def test_decl_conflict(self):

        @form.field('my-field')
        class MyField(form.Field):
            pass

        @form.field('my-field')
        class MyField2(form.Field):
            pass

        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_decl_preview(self):

        @form.field('my-field')
        class MyField(form.Field):
            pass

        @form.fieldpreview(MyField)
        def preview(request):
            """ """

        self.init_ptah()

        from ptah.form.field import PREVIEW_ID
        previews = config.get_cfg_storage(PREVIEW_ID)

        self.assertIn(MyField, previews)
        self.assertIs(previews[MyField], preview)
        self.assertIs(form.get_field_preview(MyField), preview)
