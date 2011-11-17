import signal
import sys
import unittest

from ptah import config


class TestShutdownHandlers(unittest.TestCase):

    def test_shutdown_handler(self):
        shutdownExecuted = []

        @config.shutdown_handler
        def shutdown():
            shutdownExecuted.append(True)

        shutdown = sys.modules['ptah.config.shutdown']
        shutdown._shutdown = False

        try:
            shutdown.processShutdown(signal.SIGINT, None)
        except BaseException, e:
            pass

        self.assertTrue(isinstance(e, KeyboardInterrupt))
        self.assertTrue(shutdownExecuted[0])

    def test_shutdown_exception_in_handler(self):
        shutdownExecuted = []

        @config.shutdown_handler
        def shutdown():
            raise ValueError()

        from ptah.config import shutdown
        shutdown._shutdown = False
        try:
            shutdown.processShutdown(signal.SIGINT, None)
        except BaseException, e:
            pass

        self.assertFalse(isinstance(e, ValueError))

    def test_shutdown_sigterm(self):
        shutdownExecuted = []

        @config.shutdown_handler
        def shutdown():
            shutdownExecuted.append(True)

        shutdown = sys.modules['ptah.config.shutdown']
        shutdown._shutdown = False
        try:
            shutdown.processShutdown(signal.SIGTERM, None)
        except:
            pass

        self.assertTrue(shutdownExecuted[0])
