from ptah.testing import TestCase


class StopExceptionTesting(TestCase):

    def test_api_stopexception_msg(self):
        from ptah import config

        err = config.StopException('Error message')

        self.assertEqual(str(err), '\nError message')
        self.assertEqual(err.print_tb(), 'Error message')

    def test_api_stopexception_exc(self):
        from ptah import config

        s_err = None
        try:
            raise ValueError('err')
        except Exception as exc:
            s_err = config.StopException(exc)

        self.assertIn("raise ValueError('err')", s_err.print_tb())


class LoadpackageTesting(TestCase):

    def test_stop_exc(self):
        from ptah import config

        err = ValueError('test')

        exc = config.StopException(err)
        self.assertIs(exc.exc, err)
        self.assertEqual(str(exc), '\ntest')
