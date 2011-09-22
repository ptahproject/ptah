import ptah
from ptah import View
from pyramid.security import ALL_PERMISSIONS

AddContent = ptah.Permission('ptah-cms:Add', 'Add content')
ModifyContent = ptah.Permission('ptah-cms:Edit', 'Modify content')
DeleteContent = ptah.Permission('ptah-cms:Delete', 'Delete content')

Viewer = ptah.Role('viewer', 'Viewer')
Viewer.allow(View)

Editor = ptah.Role('editor', 'Editor')
Editor.allow(View, ModifyContent)

Manager = ptah.Role('manager', 'Manager')
Manager.allow(ALL_PERMISSIONS)
