import sys
import ptah
from ptah.scripts import populate
from pyramid.compat import NativeIO


class TestPopulateCommand(ptah.PtahTestCase):

    def setUp(self):
        super(TestPopulateCommand, self).setUp()

        import ptah.scripts
        self.original_bootstrap = ptah.scripts.bootstrap

        def bootstrap(*args, **kw):
            return {'registry': self.registry, 'request': self.request,
                    'app': object()}

        ptah.scripts.bootstrap = bootstrap

    def tearDown(self):
        import ptah.scripts
        ptah.scripts.bootstrap = self.original_bootstrap

        super(TestPopulateCommand, self).tearDown()

    def test_populate_no_params(self):
        sys.argv[:] = ['ptah-populate', 'ptah.ini']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        populate.main()
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn(
            'usage: ptah-populate [-h] [-l] [-a] config [step [step ...]]', val)

    def test_populate_list(self):

        def step(registry):
            """ """

        self.config.ptah_populate_step(
            'custom-step', title='Custom step',
            active=False, factory=step)

        sys.argv[:] = ['ptah-populate', 'ptah.ini', '-l']

        stdout = sys.stdout
        out = NativeIO()
        sys.stdout = out

        populate.main()
        sys.stdout = stdout

        val = out.getvalue()

        self.assertIn('* custom-step: Custom step (inactive)', val)

    def test_populate_execute_step(self):
        data = [False]
        def step(registry):
            data[0] = True

        self.config.ptah_populate_step(
            'custom-step', title='Custom step',
            active=False, factory=step)

        sys.argv[:] = ['ptah-populate', 'ptah.ini', 'custom-step']

        populate.main()

        self.assertTrue(data[0])

    def test_populate_execute_all(self):
        data = [False, False]
        def step1(registry):
            data[0] = True

        def step2(registry): # pragma: no cover
            data[0] = True

        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1',
            active=True, factory=step1)

        self.config.ptah_populate_step(
            'custom-step2', title='Custom step 2',
            active=False, factory=step2)

        sys.argv[:] = ['ptah-populate', 'ptah.ini', '-a']

        populate.main()

        self.assertTrue(data[0])
        self.assertFalse(data[1])
