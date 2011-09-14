""" Page """
import ptah
import colander
import sqlalchemy as sqa
from webob.exc import HTTPFound
from zope import interface
from memphis import view, form

import ptah_cms
from ptah_app.permissions import AddPage

from interfaces import IPage


class PageSchema(ptah_cms.ContentSchema):

    text = colander.SchemaNode(
        colander.Str(),
        title = 'Text',
        widget = 'tinymce')


class Page(ptah_cms.Content):
    interface.implements(IPage)

    __tablename__ = 'ptah_app_pages'

    __type__ = ptah_cms.Type(
        'page', 'Page',
        add = 'addpage.html',
        schema = PageSchema,
        description = 'A page in the site.',
        )

    text = sqa.Column(sqa.Unicode)


class PageView(view.View):
    view.pyramidView('index.html', IPage, default=True,
                     permission=ptah_cms.View,
                     template=view.template('ptah_app:templates/page.pt'))



class AddPageForm(form.Form):
    view.pyramidView('addpage.html', ptah_cms.IContainer,
                     permission=AddPage)

    label = 'Add page'
    fields = form.Fields(PageSchema)

    @form.button('Add', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        page = Page(__parent__ = self.context, 
                    name = data['name'],
                    title = data['title'],
                    description = data['description'],
                    text = data['text'])
        ptah_cms.Session.add(page)

        self.message('New page has been created.')
        raise HTTPFound(location=data['name'])

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location='.')
