import unittest, signal
from memphis import config


class TestShutdownHandlers(unittest.TestCase):

    def test_shutdown_handler(self):
        shutdownExecuted = []

        @config.shutdownHandler
        def shutdown():
            shutdownExecuted.append(True)

        from memphis.config import shutdown
        shutdown._shutdown = False

        try:
            shutdown.processShutdown(signal.SIGINT, None)
        except BaseException, e:
            pass

        self.assertTrue(isinstance(e, KeyboardInterrupt))
        self.assertTrue(shutdownExecuted[0])

    def test_shutdown_exception_in_handler(self):
        shutdownExecuted = []

        @config.shutdownHandler
        def shutdown():
            raise ValueError()

        from memphis.config import shutdown
        shutdown._shutdown = False
        try:
            shutdown.processShutdown(signal.SIGINT, None)
        except BaseException, e:
            pass

        self.assertFalse(isinstance(e, ValueError))
        shutdown.handlers[:] = []

    def test_shutdown_sigterm(self):
        shutdownExecuted = []

        @config.shutdownHandler
        def shutdown():
            shutdownExecuted.append(True)

        from memphis.config import shutdown

        shutdown._shutdown = False
        try:
            shutdown.processShutdown(signal.SIGTERM, None)
        except:
            pass

        self.assertTrue(shutdownExecuted[0])
