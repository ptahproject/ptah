import sqlalchemy as sqla
import ptah
from ptah.populate import POPULATE_ID, Populate
from pyramid import testing
from pyramid.exceptions import ConfigurationConflictError


class TestPopulateDirective(ptah.PtahTestCase):

    _init_ptah = False

    def test_step_registration(self):
        import ptah

        @ptah.populate('step', title='Step', requires=['test-dep'])
        def step(registry):
            """ """

        self.init_ptah()

        data = ptah.get_cfg_storage(POPULATE_ID)

        self.assertIn('step', data)
        self.assertIs(data['step']['factory'], step)
        self.assertEqual(data['step']['title'], 'Step')
        self.assertTrue(data['step']['active'])
        self.assertEqual(data['step']['requires'], ['test-dep'])

    def test_step_pyramid_registration(self):
        import ptah

        def step(registry):
            """ """

        config = testing.setUp()
        config.include('ptah')
        config.ptah_populate_step('step', factory=step,
                                  title='Test', active=False)
        config.commit()

        data = config.get_cfg_storage(POPULATE_ID)

        self.assertIn('step', data)
        self.assertIs(data['step']['factory'], step)
        self.assertEqual(data['step']['title'], 'Test')
        self.assertFalse(data['step']['active'])
        self.assertEqual(data['step']['requires'], ())

    def test_step_registration_conflicts(self):
        import ptah

        @ptah.populate('step')
        @ptah.populate('step')
        def step(registry):
            """ """

        self.assertRaises(ConfigurationConflictError, self.init_ptah)


class TestPyramidDrective(ptah.PtahTestCase):

    def test_directive_execute(self):
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

        self.config.ptah_populate()

        self.assertTrue(data[0])
        self.assertFalse(data[1])

    def test_directive_execute_populate_mode(self):
        data = [False]
        def step(registry): # pragma: no cover
            data[0] = True

        self.config.ptah_populate_step(
            'custom-step', title='Custom step',
            active=True, factory=step)

        import ptah
        ptah.POPULATE = True

        self.config.ptah_populate()

        ptah.POPULATE = False

        self.assertFalse(data[0])


class TestListSteps(ptah.PtahTestCase):

    def test_list_simple(self):
        def step1(registry):
            """ """
        def step2(registry):
            """ """

        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1',
            active=True, factory=step1)

        self.config.ptah_populate_step(
            'custom-step2', title='Custom step 2',
            active=False, factory=step2)

        steps = Populate(self.registry).list_steps()
        steps = dict((s['name'], s) for s in steps)

        self.assertIn('custom-step1', steps)
        self.assertNotIn('custom-step2', steps)
        self.assertEqual(steps['custom-step1']['factory'], step1)

    def test_list_all(self):
        def step1(registry):
            """ """
        def step2(registry):
            """ """

        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1',
            active=True, factory=step1)

        self.config.ptah_populate_step(
            'custom-step2', title='Custom step 2',
            active=False, factory=step2)

        steps = Populate(self.registry).list_steps(all=True)
        steps = dict((s['name'], s) for s in steps)

        self.assertIn('custom-step1', steps)
        self.assertIn('custom-step2', steps)
        self.assertEqual(steps['custom-step1']['factory'], step1)
        self.assertEqual(steps['custom-step2']['factory'], step2)

    def test_list_explicit(self):
        def step1(registry):
            """ """
        def step2(registry):
            """ """

        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1',
            active=True, factory=step1)

        self.config.ptah_populate_step(
            'custom-step2', title='Custom step 2',
            active=False, factory=step2)

        steps = Populate(self.registry).list_steps(('custom-step2',))
        steps = dict((s['name'], s) for s in steps)

        self.assertNotIn('custom-step1', steps)
        self.assertIn('custom-step2', steps)

    def test_list_requires_inactive(self):
        def step1(registry):
            """ """
        def step2(registry):
            """ """
        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1',
            active=True, requires=('custom-step2',), factory=step1)
        self.config.ptah_populate_step(
            'custom-step2', title='Custom step 2',
            active=False, factory=step2)

        steps = Populate(self.registry).list_steps()
        d_steps = dict((s['name'], s) for s in steps)

        self.assertIn('custom-step1', d_steps)
        self.assertIn('custom-step2', d_steps)

    def test_list_requires_order(self):
        def step1(registry):
            """ """
        def step2(registry):
            """ """
        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1',
            active=True, requires=('custom-step2',), factory=step1)
        self.config.ptah_populate_step(
            'custom-step2', title='Custom step 2',
            active=False, factory=step2)

        steps = Populate(self.registry).list_steps()
        l_steps = [s['name'] for s in steps]

        self.assertTrue(l_steps.index('custom-step2') <
                        l_steps.index('custom-step1'))

    def test_list_once(self):
        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1', requires=('custom-step2',))
        self.config.ptah_populate_step(
            'custom-step2', title='Custom step 2')
        self.config.ptah_populate_step(
            'custom-step3', title='Custom step 3', requires=('custom-step2',))

        steps = Populate(self.registry).list_steps()

        count = 0
        for step in steps:
            if step['name'] == 'custom-step2':
                count += 1

        self.assertEqual(count, 1)

    def test_list_unknown(self):
        self.assertRaises(
            RuntimeError,
            Populate(self.registry).list_steps, ('unknown',))

    def test_list_unknown_dependency(self):
        self.config.ptah_populate_step(
            'custom-step1', title='Custom step 1', requires=('unknown',))

        self.assertRaises(
            RuntimeError, Populate(self.registry).list_steps)


class TestCreateDbSchema(ptah.PtahTestCase):

    def test_event(self):
        from ptah.populate import create_db_schema

        data = [False]
        def event_handler(ev):
            data[0] = True

        self.registry.registerHandler(
            event_handler, (ptah.events.BeforeCreateDbSchema,))

        create_db_schema(self.registry)
        self.assertTrue(data[0])

    def test_skip_tables(self):
        from ptah.populate import create_db_schema

        base = ptah.get_base()

        class test_populate_TestTable(base):
            __tablename__ = 'test_populate_TestTable'

            id = sqla.Column('id', sqla.Integer, primary_key=True)

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH)
        cfg['db_skip_tables'] = ('test_populate_TestTable',)

        create_db_schema(self.registry)

        self.assertFalse(
            base.metadata.tables['test_populate_TestTable'].exists())

        cfg['db_skip_tables'] = ()
        create_db_schema(self.registry)

        self.assertTrue(
            base.metadata.tables['test_populate_TestTable'].exists())
