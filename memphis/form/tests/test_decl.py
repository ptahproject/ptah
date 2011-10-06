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
