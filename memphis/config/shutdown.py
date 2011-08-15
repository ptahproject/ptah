""" process shutdown """
import sys, signal, logging


handlers = []

def shutdownHandler(handler):
    handlers.append(handler)
    return handler


_shutdown = False
_handler_int = signal.getsignal(signal.SIGINT)

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

    if sig == signal.SIGINT and callable(_handler_int):
        _handler_int()


signal.signal(signal.SIGINT, processShutdown)
