""" Page """
import ptah
import sqlalchemy as sqla

import ptah_cms
from ptah_app.permissions import AddPage


class Page(ptah_cms.Content):

    __tablename__ = 'ptah_app_pages'

    __type__ = ptah_cms.Type(
        'page',
        title = 'Page',
        description = 'A page in the site.',
        permission = AddPage,
        name_suffix = '.html',
        )

    text = sqla.Column(sqla.Unicode,
                       info = {'field_type': 'tinymce'})


ptah.view.register_view(
    context = Page,
    permission = ptah_cms.View,
    template = ptah.view.template('ptah_app:templates/page.pt'))
