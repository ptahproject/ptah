import ptah
from ptah import security
from ptah.security import View
from pyramid.security import ALL_PERMISSIONS

AddContent = security.Permission('ptah-cms:Add', 'Add content')
ModifyContent = security.Permission('ptah-cms:Edit', 'Modify content')
DeleteContent = security.Permission('ptah-cms:Delete', 'Delete content')

Viewer = security.registerRole('viewer', 'Viewer')
Viewer.allow(View)

Editor = security.registerRole('editor', 'Editor')
Editor.allow(View, ModifyContent)

Manager = security.registerRole('manager', 'Manager')
Manager.allow(ALL_PERMISSIONS)
