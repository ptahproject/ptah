from memphis import form, config

from base import Base


class TestFieldset(Base):

    def test_decl(self):
        global MyField

        class MyField(form.Field):

            form.field('my-field')

        self._init_memphis()
        self.assertIs(form.get_field_factory('my-field'), MyField)

    def test_decl_register(self):

        class MyField(form.Field):
            """ """

        form.register_field_factory(MyField, 'my-field')

        self._init_memphis()
        self.assertIs(form.get_field_factory('my-field'), MyField)

    def test_decl_conflict(self):
        global MyField, MyField2

        class MyField(form.Field):

            form.field('my-field')


        class MyField2(form.Field):

            form.field('my-field')

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_decl_preview(self):
        global MyField

        class MyField(form.Field):
            form.field('my-field')

        @form.fieldpreview(MyField)
        def preview(request):
            """ """

        self._init_memphis()

        from memphis.form.field import PREVIEW_ID
        previews = config.registry.storage[PREVIEW_ID]

        self.assertIn(MyField, previews)
        self.assertIs(previews[MyField], preview)
