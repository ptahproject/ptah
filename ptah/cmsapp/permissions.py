""" app permissions and roles """
import ptah
from pyramid.security import ALL_PERMISSIONS

AddPage = ptah.Permission('ptah-app: Add page', 'Add page')
AddFile = ptah.Permission('ptah-app: Add file', 'Add file')
AddFolder = ptah.Permission('ptah-app: Add folder', 'Add folder')

ptah.Everyone.allow(ptah.cms.View)
ptah.Authenticated.allow(ptah.cms.AddContent)

Viewer = ptah.Role('viewer', 'Viewer')
Viewer.allow(ptah.cms.View)

Editor = ptah.Role('editor', 'Editor')
Editor.allow(ptah.cms.View, ptah.cms.ModifyContent)

Manager = ptah.Role('manager', 'Manager')
Manager.allow(ALL_PERMISSIONS)

ptah.Owner.allow(ptah.cms.DeleteContent)
