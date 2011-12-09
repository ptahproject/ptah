# ptah.view API !!! PRIVATE API !!! basically it is mimic core pyramid api

# static resources
from ptah.view.resources import static
from ptah.view.resources import static_url

# resource library
from ptah.view.library import library
from ptah.view.library import include
from ptah.view.library import render_includes

# base view
from ptah.view.base import View

# snippet
from ptah.view.snippet import snippet
from ptah.view.snippet import Snippet
from ptah.view.snippet import snippettype
from ptah.view.snippet import render_snippet
from ptah.view.snippet import register_snippet

# layout
from ptah.view.layout import layout
from ptah.view.layout import Layout
from ptah.view.layout import LayoutRenderer
from ptah.view.layout import query_layout
from ptah.view.layout import query_layout_chain
from ptah.view.layout import register_layout

# status message
from ptah.view.message import Message
from ptah.view.message import add_message
from ptah.view.message import render_messages
from ptah.view.message import get_message_service
