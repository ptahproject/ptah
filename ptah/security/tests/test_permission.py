from zope import interface
from memphis import config
from pyramid.security import ALL_PERMISSIONS

from base import Base


class Permission(Base):

    def test_permission_register(self):
        import ptah

        perm = ptah.Permission('perm', 'Permission', 'Test permission')
       
        self.assertTrue(perm == 'perm')
        self.assertTrue(perm.title == 'Permission')
        self.assertTrue(perm.description == 'Test permission')
        self.assertTrue(ptah.Permissions['perm'] is perm)

    def test_permission_register_same_name(self):
        import ptah

        perm = ptah.Permission('perm', 'Permission1')
        perm2 = ptah.Permission('perm', 'Permission2')

        self.assertRaises(config.ConflictError, self._init_memphis)


class PermissionsMap(Base):

    def test_permissionsmap_register(self):
        import ptah

        pmap = ptah.PermissionsMap('map', 'permissions', 'Map')
        
        self.assertTrue(pmap.name == 'map')
        self.assertTrue(pmap.title == 'permissions')
        self.assertTrue(pmap.description == 'Map')
        self.assertTrue(ptah.PermissionsMaps['map'] is pmap)

    def test_permissionsmap_register_same_name(self):
        import ptah

        pmap = ptah.PermissionsMap('map', 'permissions1')
        pmap2 = ptah.PermissionsMap('map', 'permissions2')

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_permissionsmap_allow(self):
        import ptah

        pmap = ptah.PermissionsMap('map', 'permissions')

        role = ptah.Role('test', 'test')

        pmap.allow(role, 'perm1')
        pmap.allow('role:test', 'perm2')

        self.assertEqual(pmap.allowed['role:test'], set(('perm2', 'perm1')))

    def test_permissionsmap_deny(self):
        import ptah

        pmap = ptah.PermissionsMap('map', 'permissions')

        role = ptah.Role('test', 'test')

        pmap.deny(role, 'perm1')
        pmap.deny('role:test', 'perm2')

        self.assertEqual(pmap.denied['role:test'], set(('perm2', 'perm1')))
