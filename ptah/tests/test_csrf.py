from ptah.testing import PtahTestCase


class TestCsrf(PtahTestCase):

    def test_csrf_service(self):
        from ptah.util import CSRFService

        csrf = CSRFService()
        t = csrf.generate('test')

        self.assertEqual(csrf.get(t), 'test')
        self.assertEqual(csrf.generate('test'), t)

        csrf.remove(t)
        self.assertEqual(csrf.get(t), None)

        t2 = csrf.generate('test')
        self.assertTrue(t != t2)
