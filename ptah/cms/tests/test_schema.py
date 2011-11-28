from ptah.testing import PtahTestCase


class TestNameSchema(PtahTestCase):

    def test_schema_name_validator(self):
        from ptah.cms.interfaces import ContentNameSchema

        fieldset = ContentNameSchema.bind(
            params = {'__name__': '/asdfasdfadf'})

        data, errors = fieldset.extract()
        self.assertTrue(errors)

        fieldset = ContentNameSchema.bind(
            params = {'__name__': 'asdfasdf/adf'})

        data, errors = fieldset.extract()
        self.assertTrue(errors)

        fieldset = ContentNameSchema.bind(
            params = {'__name__': ' asdfasdfadf'})

        data, errors = fieldset.extract()
        self.assertTrue(errors)
