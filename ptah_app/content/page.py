""" Page """
import colander
import sqlalchemy as sqla
from zope import interface
from memphis import view, form

import ptah_cms
from ptah_app import AddForm
from ptah_app.permissions import AddPage

from interfaces import IPage


class Page(ptah_cms.Content):
    interface.implements(IPage)

    __tablename__ = 'ptah_app_pages'

    __type__ = ptah_cms.Type(
        'page', 'Page',
        add = 'addpage.html',
        description = 'A page in the site.',
        permission = AddPage,
        name_suffix = '.html',
        )

    text = sqla.Column(sqla.Unicode,
                       info = {'field_type': 'tinymce'})


view.registerView(context=IPage,
                  permission=ptah_cms.View,
                  template=view.template('ptah_app:templates/page.pt'))

class AddPageForm(AddForm):
    view.pyramidView('addpage.html', ptah_cms.IContainer, permission=AddPage)

    tinfo = Page.__type__

