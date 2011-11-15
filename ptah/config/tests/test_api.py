import unittest


class StopExceptionTesting(unittest.TestCase):

    def test_api_stopexception_msg(self):
        from ptah.config import api

        err = api.StopException('Error message')

        self.assertEqual(str(err), '\nError message')
        self.assertEqual(err.print_tb(), 'Error message')

    def test_api_stopexception_exc(self):
        from ptah.config import api

        try:
            raise ValueError('err')
        except Exception, exc:
            pass

        err = api.StopException(exc)

        self.assertIn("raise ValueError('err')", err.print_tb())


class LoadpackageTesting(unittest.TestCase):

    def test_exclude_test(self):
        from ptah.config import api

        self.assertFalse(api.exclude('blah.test'))
        self.assertFalse(api.exclude('blah.ftest'))
        self.assertFalse(api.exclude('blah.subpkg', ('blah.',)))
        self.assertTrue(api.exclude('blah.subpkg'))

    def test_loadpackages(self):
        from ptah.config import api

        self.assertEqual(
            api.list_packages(('ptah',), excludes=('ptah',)), [])

        self.assertIn('ptah', api.list_packages())
        self.assertEqual(api.list_packages(excludes=('ptah',)), [])

    def test_stop_exc(self):
        from ptah.config import api

        err = ValueError('test')

        exc = api.StopException(err)
        self.assertIs(exc.exc, err)
        self.assertEqual(str(exc), '\ntest')
