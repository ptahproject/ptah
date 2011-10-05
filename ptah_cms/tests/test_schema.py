import unittest
from memphis import form


class TestNameSchema(unittest.TestCase):

    def test_schema_name_validator(self):
        from ptah_cms.interfaces import ContentNameSchema
        schema = ContentNameSchema()

        self.assertRaises(
            form.Invalid,
            schema.deserialize, {'__name__': '/asdfasdfadf'})

        self.assertRaises(
            form.Invalid,
            schema.deserialize, {'__name__': 'asdfasdf/adf'})

        self.assertRaises(
            form.Invalid,
            schema.deserialize, {'__name__': ' asdfasdfadf'})
