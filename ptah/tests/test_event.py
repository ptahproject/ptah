import ptah
from pyramid.exceptions import ConfigurationConflictError


class TestEvent(ptah.PtahTestCase):

    _init_ptah = False

    def test_event_registration(self):
        import ptah

        @ptah.event('TestEvent')
        class TestEvent(object):
            """ test event """

        self.init_ptah()

        storage = self.config.get_cfg_storage(ptah.event.ID_EVENT)

        self.assertIn(TestEvent, storage)
        ev = storage[TestEvent]
        self.assertIn(ev.name, storage)

    def test_event_registration_dupl(self):
        import ptah

        @ptah.event('TestEvent')
        class TestEvent1(object):
            """ test event """

        @ptah.event('TestEvent')
        class TestEvent2(object):
            """ test event """

        self.config.scan('ptah')
        self.config.scan(self.__class__.__module__)
        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_event_intr(self):
        import ptah

        @ptah.event('TestEvent')
        class TestEvent(object):
            """ test event """

        self.init_ptah()

        name = '{0}.{1}'.format(TestEvent.__module__, TestEvent.__name__)

        intr = self.registry.introspector.get(
            ptah.event.ID_EVENT,
            (ptah.event.ID_EVENT, name))
        self.assertIsNotNone(intr)
        self.assertIs(intr['ev'].factory, TestEvent)
