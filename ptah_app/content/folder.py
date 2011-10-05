""" Generic folder implementation """
from zope import interface
from memphis import view, form

import ptah_cms, ptah_app
from ptah_app.permissions import AddFolder

from interfaces import IFolder


class Folder(ptah_cms.Container):
    interface.implements(IFolder)

    __type__ = ptah_cms.Type(
        'folder', 'Folder',
        add = 'addfolder.html',
        description = 'A folder which can contain other items.',
        permission = AddFolder,
        )


class AddFolderForm(ptah_app.AddForm):
    view.pyramidView('addfolder.html', ptah_cms.IContainer)

    tinfo = Folder.__type__
