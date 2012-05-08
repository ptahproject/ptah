# sockjs

try:
    from .form import Form
    from .protocol import handler
    from .protocol import protocol
    from .protocol import Protocol

    from .session import Session
    from .session import get_session_manager
except ImportError:
    pass


def register_ptah_sm(cfg, session=None):
    # sockjs connection
    from .session import SessionManager
    cfg.add_sockjs_route(
        'ptah', '/_ptah_connection',
        session_manager=SessionManager('ptah', cfg.registry, session))
