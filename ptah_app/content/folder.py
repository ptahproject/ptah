""" Generic folder implementation """
import colander
from webob.exc import HTTPFound
from zope import interface
from memphis import view, form

import ptah_cms
from ptah_app.permissions import AddFolder

from interfaces import IFolder


class FolderSchema(colander.Schema):

    name = colander.SchemaNode(
        colander.Str(),
        title = 'Name')

    title = colander.SchemaNode(
        colander.Str(),
        title = 'Title')

    description = colander.SchemaNode(
        colander.Str(),
        title = 'Description',
        widget = 'textarea')

    
class Folder(ptah_cms.Container):
    interface.implements(IFolder)

    __type__ = ptah_cms.Type(
        'folder', 'Folder',
        add = 'addfolder.html',
        description = 'A folder which can contain other items.',
        )


class AddFolderForm(form.Form):
    view.pyramidView('addfolder.html', ptah_cms.IContainer,
                     permission=AddFolder)

    label = 'Add folder'
    fields = form.Fields(ptah_cms.ContentSchema)

    @form.button('Add', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        folder = Folder(__parent__ = self.context, 
                        name = data['name'],
                        title = data['title'],
                        description = data['description'])
        ptah_cms.Session.add(folder)

        self.message('New folder has been created.')
        raise HTTPFound(location='%s/'%data['name'])

    @form.button('Cancel')
    def cancelHandler(self):
        pass
