from datetime import datetime
from ptah.testing import TestCase


class TestJson(TestCase):

    def test_datetime(self):
        from ptah import util
        dt = datetime(2011, 10, 1, 1, 56)

        self.assertEqual(util.dthandler(dt), 'Sat, 01 Oct 2011 01:56:00 -0000')
        self.assertIsNone(util.dthandler(object()))

    def test_json(self):
        from ptah import util

        data = {'date': datetime(2011, 10, 1, 1, 56),
                'int': 10,
                'str': 'string'}

        self.assertEqual(
            util.json.dumps(data),
            '{"date":"Sat, 01 Oct 2011 01:56:00 -0000","int":10,"str":"string"}')

        self.assertEqual(
            util.json.loads('{"int":10,"str":"string"}'),
            {'int': 10, 'str': 'string'})
