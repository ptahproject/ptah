""" process shutdown """
import logging
import signal
import sys

from signal import SIGINT, SIGTERM

handlers = []


def shutdown_handler(handler):
    handlers.append(handler)
    return handler


_shutdown = False
_handler_int = signal.getsignal(SIGINT)
_handler_term = signal.getsignal(SIGTERM)
log = logging.getLogger('ptah.config')


def shutdown():
    global _shutdown

    if not _shutdown:
        #_shutdown = True

        for handler in handlers:
            try:
                handler()
            except:
                #log.exception("Showndown handler: %s"%handler)
                pass

    #handlers[:] = []


def processShutdown(sig, frame):
    shutdown()

    if sig == SIGINT and callable(_handler_int):
        _handler_int(sig, frame)

    if sig == SIGTERM and callable(_handler_term):  # pragma: no cover
        _handler_term(sig, frame)

    if sig == SIGTERM:
        raise sys.exit()


try:
    import mod_wsgi
except ImportError:
    signal.signal(SIGINT, processShutdown)
    signal.signal(SIGTERM, processShutdown)
