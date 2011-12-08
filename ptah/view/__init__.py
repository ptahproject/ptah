# ptah.view API !!! PRIVATE API !!! basically it is mimic core pyramid api

# static resources
from ptah.view.resources import static
from ptah.view.resources import static_url

# resource library
from ptah.view.library import library
from ptah.view.library import include
from ptah.view.library import render_includes

# path/template
from ptah.view.tmpl import path, template

# base view
from ptah.view.base import View

# snippet
from ptah.view.snippet import snippet
from ptah.view.snippet import Snippet
from ptah.view.snippet import snippettype
from ptah.view.snippet import render_snippet
from ptah.view.snippet import register_snippet

# route
from ptah.view.route import register_route

# layout
from ptah.view.layout import layout
from ptah.view.layout import Layout
from ptah.view.layout import LayoutRenderer
from ptah.view.layout import query_layout
from ptah.view.layout import query_layout_chain
from ptah.view.layout import register_layout

# view
from ptah.view.view import pview
from ptah.view.view import render_view
from ptah.view.view import register_view
from ptah.view.renderers import set_checkpermission
from ptah.view.renderers import ViewRenderer
from ptah.view.renderers import TemplateRenderer

# status message
from ptah.view.message import Message
from ptah.view.message import add_message
from ptah.view.message import render_messages
from ptah.view.message import get_message_service
