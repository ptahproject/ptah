from memphis import form, config

from base import Base


class TestFieldset(Base):

    def test_decl(self):
        global MyField

        class MyField(form.Field):

            form.field('my-field')

        self._init_memphis()
        self.assertIs(form.getField('my-field'), MyField)

    def test_decl_register(self):

        class MyField(form.Field):
            """ """
            
        form.registerField(MyField, 'my-field')

        self._init_memphis()
        self.assertIs(form.getField('my-field'), MyField)

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

        @form.fieldPreview(MyField)
        def preview(request):
            """ """

        self._init_memphis()

        from memphis.form.field import previews
        self.assertIn(MyField, previews)
        self.assertIs(previews[MyField], preview)
