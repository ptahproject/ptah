""" default actions """
import ptah, ptah_cms, ptah_app

ptah_app.uiaction(
    ptah_cms.IContent, **{'id': 'view',
                          'title': 'View',
                          'action': '',
                          'permission': ptah_cms.View,
                          'sortWeight': 0.5})

ptah_app.uiaction(
    ptah_cms.IContent, **{'id': 'edit',
                          'title': 'Edit',
                          'action': 'edit.html',
                          'permission': ptah_cms.ModifyContent,
                          'sortWeight': 0.6})


ptah_app.uiaction(
    ptah_cms.IContainer, **{'id': 'adding',
                            'title': 'Add content',
                            'action': '+/',
                            'permission': ptah_cms.AddContent,
                            'sortWeight': 5.0})


ptah_app.uiaction(
    ptah.ILocalRolesAware, **{'id': 'sharing',
                              'title': 'Sharing',
                              'action': 'sharing.html',
                              'permission': ptah_cms.ShareContent,
                              'sortWeight': 10.0})
