# sockjs

try:
    from .form import Form
    from .protocol import handler
    from .protocol import protocol
    from .protocol import Protocol

    from .session import Session
    from .session import get_session_manager
except ImportError: # pragma: no cover
    pass


def register_ptah_sm(cfg, session=None, **kw):
    # sockjs connection
    from .session import SessionManager
    kw['session_manager'] = SessionManager('ptah', cfg.registry, session)
    cfg.add_sockjs_route('ptah', '/_ptah_connection', **kw)
