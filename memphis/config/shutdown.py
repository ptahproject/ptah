""" process shutdown """
import sys, signal, logging
from signal import SIGINT, SIGTERM

handlers = []

def shutdownHandler(handler):
    handlers.append(handler)
    return handler


_shutdown = False
_handler_int = signal.getsignal(SIGINT)
_handler_term = signal.getsignal(SIGTERM)
log = logging.getLogger('memphis.config')


def processShutdown(sig, frame):
    global _shutdown

    if not _shutdown:
        _shutdown = True
        for handler in handlers:
            try:
                handler()
            except:
                log.exception("Showndown handler: %s"%handler)

    if sig == SIGINT and callable(_handler_int):
        _handler_int(sig, frame)

    if sig == SIGTERM and callable(_handler_term): # pragma: no cover
        _handler_term(sig, frame)

    if sig == SIGTERM:
        raise sys.exit()


try:
    import mod_wsgi
except ImportError:
    signal.signal(SIGINT, processShutdown)
    signal.signal(SIGTERM, processShutdown)
