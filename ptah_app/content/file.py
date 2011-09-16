""" file content implementation """
import colander
import sqlalchemy as sqla
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from zope import interface
from memphis import view, form

import ptah
import ptah_cms
from ptah_app.permissions import AddFile

from interfaces import IFile


class FileSchema(ptah_cms.ContentSchema):

    data = colander.SchemaNode(
        colander.Str(),
        title = 'Data',
        widget = 'file')


class File(ptah_cms.Content):
    interface.implements(IFile)

    __tablename__ = 'ptah_app_files'

    __type__ = ptah_cms.Type(
        'file', 'File',
        add = 'addfile.html',
        schema = FileSchema,
        description = 'A file in the site.',
        )

    blobref = sqla.Column(sqla.Unicode)


class FileView(view.View):
    view.pyramidView('index.html', IFile, default=True,
                     permission=ptah_cms.View,
                     template=view.template('ptah_app:templates/file.pt'))

    def update(self):
        self.resolve = ptah.resolve


class FileDownloadView(view.View):
    view.pyramidView('download.html', IFile, layout=None,
                     permission=ptah_cms.View)

    def render(self):
        blob = ptah.resolve(self.context.blobref)

        response = self.request.response
        response.content_type = blob.mimetype
        if blob.filename:
            response.headerlist = {
                'Content-Disposition': 'filename="%s"'%blob.filename}
        response.body = blob.read()
        return response


class FileAddForm(ptah_cms.AddForm):
    view.pyramidView('addfile.html', ptah_cms.IContainer, permission=AddFile)

    label = 'Add file'
    fields = form.Fields(FileSchema)

    @form.button('Add', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        file = File(title = data['title'],
                    description = data['description'])
        ptah_cms.Session.add(file)
        ptah_cms.Session.flush()

        fd = data['data']
        blob_uuid = ptah_cms.blobStorage.add(
            fd['fp'], file,
            filename = fd['filename'],
            mimetype = fd['mimetype'])

        file.blobref = blob_uuid

        self.request.registry.notify(
            ptah_cms.events.ContentCreatedEvent(page))

        self.context[data['__name__']] = file

        self.message('New file has been created.')
        raise HTTPFound(location='%s/index.html'%data['__name__'])

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location='.')


class FileEditForm(form.Form):
    view.pyramidView('edit.html', IFile,
                     permission=ptah_cms.ModifyContent)

    label = 'Modify file'
    fields = form.Fields(FileSchema)

    def getContent(self):
        return self.context

    @form.button('Save', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        fd = data['data']
        if fd:
            blob = ptah.resolve(self.context.blobref)
            blob.write(fd['fp'].read())
            blob.updateMetadata(
                filename = fd['filename'],
                mimetype = fd['mimetype'])

        self.context.name = data['name']
        self.context.title = data['title']
        self.context.description = data['description']

        self.message('Changes have been saved.')
        raise HTTPFound(location='.')

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location='.')
