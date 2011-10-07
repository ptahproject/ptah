""" Page """
import memphis
import sqlalchemy as sqla

import ptah_cms
from ptah_app.permissions import AddPage


class Page(ptah_cms.Content):

    __tablename__ = 'ptah_app_pages'

    __type__ = ptah_cms.Type(
        'page', 'Page',
        description = 'A page in the site.',
        permission = AddPage,
        name_suffix = '.html',
        )

    text = sqla.Column(sqla.Unicode,
                       info = {'field_type': 'tinymce'})

    test_title = sqla.Column(sqla.Unicode)


memphis.view.registerView(
    context = Page,
    permission = ptah_cms.View,
    template = memphis.view.template('ptah_app:templates/page.pt'))
