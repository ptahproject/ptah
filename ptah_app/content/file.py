""" file content implementation """
import colander
import sqlalchemy as sqla
from pyramid.httpexceptions import HTTPNotFound

from zope import interface
from memphis import view, form

import ptah, ptah_cms, ptah_app
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

    @ptah_cms.action('update', IFile, ptah_cms.ModifyContent, "Update file")
    def update(self, **data):
        fd = data['data']
        if fd:
            blob = ptah.resolve(self.blobref)
            if blob is None:
                blob = ptah_cms.blobStorage.create(self)
                self.blobref = blob.__uri__

            blob.write(fd['fp'].read())
            blob.updateMetadata(
                filename = fd['filename'],
                mimetype = fd['mimetype'])

        self.title = data['title']
        self.description = data['description']


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
                'Content-Disposition': 
                'filename="%s"'%blob.filename.encode('utf-8')}
        response.body = blob.read()
        return response


class FileAddForm(ptah_app.AddForm):
    view.pyramidView('addfile.html', ptah_cms.IContainer)

    tinfo = File.__type__
    fields = form.Fields(FileSchema)

    def chooseName(self, **kw):
        filename = kw['data']['filename']
        name = filename.split('\\')[-1].split('/')[-1]

        i = 1
        n = name
        while n in self.container:
            i += 1
            n = u'%s-%s'%(name, i)

        return n
