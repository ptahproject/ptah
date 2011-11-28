from ptah import form, config
from ptah.testing import PtahTestCase


class TestFieldset(PtahTestCase):

    _init_ptah = False

    def test_decl(self):
        global MyField

        class MyField(form.Field):

            form.field('my-field')

        self.init_ptah()
        self.assertIs(form.get_field_factory('my-field'), MyField)

    def test_decl_register(self):

        class MyField(form.Field):
            """ """

        form.register_field_factory(MyField, 'my-field')

        self.init_ptah()
        self.assertIs(form.get_field_factory('my-field'), MyField)

    def test_decl_conflict(self):
        global MyField, MyField2

        class MyField(form.Field):

            form.field('my-field')


        class MyField2(form.Field):

            form.field('my-field')

        self.assertRaises(config.ConflictError, self.init_ptah)

    def test_decl_preview(self):
        global MyField

        class MyField(form.Field):
            form.field('my-field')

        @form.fieldpreview(MyField)
        def preview(request):
            """ """

        self.init_ptah()

        from ptah.form.field import PREVIEW_ID
        previews = config.get_cfg_storage(PREVIEW_ID)

        self.assertIn(MyField, previews)
        self.assertIs(previews[MyField], preview)
        self.assertIs(form.get_field_preview(MyField), preview)
