""" Generic folder implementation """
import ptah_cms
from ptah_app.permissions import AddFolder


class Folder(ptah_cms.Container):

    __type__ = ptah_cms.Type(
        'folder', 'Folder',
        description = 'A folder which can contain other items.',
        permission = AddFolder)
