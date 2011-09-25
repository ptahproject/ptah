""" file content implementation """
import colander
import sqlalchemy as sqla
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from zope import interface
from memphis import view, form

import ptah
import ptah_cms
from ptah_app import AddForm
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
        permission = AddFile,
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
        if blob is None:
            raise HTTPNotFound()

        response = self.request.response
        response.content_type = blob.mimetype
        if blob.filename:
            response.headerlist = {
                'Content-Disposition': 'filename="%s"'%blob.filename}
        response.body = blob.read()
        return response


class FileAddForm(AddForm):
    view.pyramidView('addfile.html', ptah_cms.IContainer)

    tinfo = File.__type__
    fields = form.Fields(FileSchema)

    def chooseName(self, content, **kw):
        filename = kw['data']['filename']
        name = filename.split('\\')[-1].split('/')[-1]

        i = 1
        n = name
        while n in self.container:
            i += 1
            n = u'%s-%s'%(name, i)

        return n

    def create(self, **data):
        file = File(title = data['title'],
                    description = data['description'])
        ptah_cms.Session.add(file)
        ptah_cms.Session.flush()

        fd = data['data']
        blob = ptah_cms.blobStorage.add(
            fd['fp'], file,
            filename = fd['filename'],
            mimetype = fd['mimetype'])

        file.blobref = blob.__uuid__
        return file


class FileEditForm(form.Form):
    view.pyramidView('edit.html', IFile,
                     permission=ptah_cms.ModifyContent)

    label = 'Modify file'
    fields = form.Fields(FileSchema)

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

        self.context.title = data['title']
        self.context.description = data['description']

        self.message('Changes have been saved.')
        raise HTTPFound(location='.')
