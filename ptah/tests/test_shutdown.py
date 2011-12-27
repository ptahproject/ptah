import signal
import sys
from ptah import config
from ptah.testing import TestCase


class TestShutdownHandlers(TestCase):

    def test_shutdown_handler(self):
        shutdownExecuted = []

        @config.shutdown_handler
        def shutdown():
            shutdownExecuted.append(True)

        shutdown = sys.modules['ptah.config']
        shutdown._shutdown = False

        err = None
        try:
            shutdown.process_shutdown(signal.SIGINT, None)
        except BaseException as e:
            err = e

        self.assertTrue(isinstance(err, KeyboardInterrupt))
        self.assertTrue(shutdownExecuted[0])

    def test_shutdown_exception_in_handler(self):
        shutdownExecuted = []

        @config.shutdown_handler
        def shutdown():
            raise ValueError()

        from ptah.config import shutdown
        shutdown._shutdown = False

        err = None
        try:
            shutdown.process_shutdown(signal.SIGINT, None)
        except BaseException as e:
            err = e

        self.assertFalse(isinstance(err, ValueError))

    def test_shutdown_sigterm(self):
        shutdownExecuted = []

        @config.shutdown_handler
        def shutdown():
            shutdownExecuted.append(True)

        shutdown = sys.modules['ptah.config']
        shutdown._shutdown = False
        try:
            shutdown.process_shutdown(signal.SIGTERM, None)
        except:
            pass

        self.assertTrue(shutdownExecuted[0])
