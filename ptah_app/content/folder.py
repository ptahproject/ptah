""" Generic folder implementation """
import colander
from zope import interface
from memphis import view, form
from pyramid.httpexceptions import HTTPFound

import ptah_cms
from ptah_app import AddForm
from ptah_app.permissions import AddFolder

from interfaces import IFolder


class Folder(ptah_cms.Container):
    interface.implements(IFolder)

    __type__ = ptah_cms.Type(
        'folder', 'Folder',
        add = 'addfolder.html',
        description = 'A folder which can contain other items.',
        )


class AddFolderForm(AddForm):
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

        folder = Folder(title = data['title'],
                        description = data['description'])
        ptah_cms.Session.add(folder)

        self.request.registry.notify(
            ptah_cms.events.ContentCreatedEvent(folder))

        self.context[data['__name__']] = folder

        self.message('New folder has been created.')
        raise HTTPFound(location='%s/'%data['__name__'])

    @form.button('Cancel')
    def cancelHandler(self):
        pass
