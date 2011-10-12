""" role """
from zope import interface
from memphis import config
from pyramid.security import Allow, Deny, ALL_PERMISSIONS, DENY_ALL
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import HTTPForbidden

from base import Base


class TestPermission(Base):

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


class TestACL(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestACL, self).tearDown()

    def test_acl_register(self):
        import ptah

        pmap = ptah.ACL('map', 'ACL', 'Map')

        self.assertTrue(pmap.name == 'map')
        self.assertTrue(pmap.title == 'ACL')
        self.assertTrue(pmap.description == 'Map')
        self.assertTrue(ptah.ACLs['map'] is pmap)

    def test_acl_register_same_name(self):
        import ptah

        pmap1 = ptah.ACL('map', 'acl1')
        pmap2 = ptah.ACL('map', 'acl2')

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_acl_allow(self):
        import ptah

        role = ptah.Role('test', 'test')

        pmap = ptah.ACL('map', 'acl map')
        pmap.allow(role, 'perm1')
        pmap.allow('role:test', 'perm2')

        self.assertEqual(len(pmap), 1)
        self.assertEqual(pmap[0][0], Allow)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], set(('perm2', 'perm1')))

    def test_acl_allow_all(self):
        import ptah

        role = ptah.Role('test', 'test')

        pmap = ptah.ACL('map', 'acl map')
        pmap.allow(role, 'perm1')
        pmap.allow(role, ALL_PERMISSIONS)
        pmap.allow(role, 'perm2')

        self.assertEqual(len(pmap), 1)
        self.assertEqual(pmap[0][0], Allow)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], ALL_PERMISSIONS)

    def test_acl_deny(self):
        import ptah

        role = ptah.Role('test', 'test')

        pmap = ptah.ACL('map', 'acl map')
        pmap.deny(role, 'perm1')
        pmap.deny('role:test', 'perm2')

        self.assertEqual(len(pmap), 1)
        self.assertEqual(pmap[0][0], Deny)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], set(('perm2', 'perm1')))

    def test_acl_deny_all(self):
        import ptah

        pmap = ptah.ACL('map', 'acl map')
        pmap.deny('role:test', 'perm1')
        pmap.deny('role:test', ALL_PERMISSIONS)
        pmap.deny('role:test', 'perm2')

        self.assertEqual(len(pmap), 1)
        self.assertEqual(pmap[0][0], Deny)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], ALL_PERMISSIONS)

    def test_acl_order(self):
        import ptah

        pmap = ptah.ACL('map', 'acl map')
        pmap.deny('role:test', 'perm1')
        pmap.allow('role:test', 'perm2')
        pmap.allow('role:test2', 'perm2')
        pmap.deny('role:test2', 'perm2')

        self.assertEqual(pmap[0][0], Deny)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[1][0], Allow)
        self.assertEqual(pmap[1][1], 'role:test')
        self.assertEqual(pmap[2][0], Allow)
        self.assertEqual(pmap[2][1], 'role:test2')
        self.assertEqual(pmap[3][0], Deny)
        self.assertEqual(pmap[3][1], 'role:test2')

    def test_acl_unset_allow(self):
        import ptah

        role = ptah.Role('test', 'test')

        pmap = ptah.ACL('map', 'acl map')
        pmap.allow(role, 'perm1', 'perm2')
        pmap.allow('role:test2', 'perm1')

        pmap.unset(None, 'perm1')

        self.assertEqual(len(pmap), 1)
        self.assertEqual(pmap[0][0], Allow)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], set(('perm2',)))

    def test_acl_unset_role_allow(self):
        import ptah

        role = ptah.Role('test', 'test')

        pmap = ptah.ACL('map', 'acl map')
        pmap.allow(role, 'perm1', 'perm2')
        pmap.allow('role:test2', 'perm1')

        pmap.unset(role.id, 'perm1')

        self.assertEqual(len(pmap), 2)
        self.assertEqual(pmap[0][0], Allow)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], set(('perm2',)))
        self.assertEqual(pmap[1][0], Allow)
        self.assertEqual(pmap[1][1], 'role:test2')
        self.assertEqual(pmap[1][2], set(('perm1',)))

    def test_acl_unset_deny(self):
        import ptah

        role = ptah.Role('test', 'test')

        pmap = ptah.ACL('map', 'acl map')
        pmap.deny(role, 'perm1', 'perm2')
        pmap.deny('role:test2', 'perm1')

        pmap.unset(None, 'perm1')

        self.assertEqual(len(pmap), 1)
        self.assertEqual(pmap[0][0], Deny)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], set(('perm2',)))

    def test_acl_unset_role_deny(self):
        import ptah

        role = ptah.Role('test', 'test')

        pmap = ptah.ACL('map', 'acl map')
        pmap.deny(role, 'perm1', 'perm2')
        pmap.deny('role:test2', 'perm1')

        pmap.unset(role.id, 'perm1')

        self.assertEqual(len(pmap), 2)
        self.assertEqual(pmap[0][0], Deny)
        self.assertEqual(pmap[0][1], 'role:test')
        self.assertEqual(pmap[0][2], set(('perm2',)))
        self.assertEqual(pmap[1][0], Deny)
        self.assertEqual(pmap[1][1], 'role:test2')
        self.assertEqual(pmap[1][2], set(('perm1',)))

    def test_acl_unset_all(self):
        import ptah

        pmap = ptah.ACL('map', 'acl map')
        pmap.allow('role:test1', 'perm1', 'perm2')
        pmap.allow('role:test2', 'perm1')
        pmap.deny('role:test1', 'perm1', 'perm2')
        pmap.deny('role:test2', ALL_PERMISSIONS)

        pmap.unset(None, ALL_PERMISSIONS)
        self.assertEqual(len(pmap), 0)

    def test_acl_unset_role_all(self):
        import ptah

        pmap = ptah.ACL('map', 'acl map')
        pmap.allow('role:test1', 'perm2')
        pmap.allow('role:test2', 'perm1')
        pmap.deny('role:test1', 'perm1', 'perm2')
        pmap.deny('role:test2', ALL_PERMISSIONS)

        pmap.unset('role:test2', ALL_PERMISSIONS)
        self.assertEqual(len(pmap), 2)
        self.assertEqual(pmap[0][0], Allow)
        self.assertEqual(pmap[0][1], 'role:test1')
        self.assertEqual(pmap[0][2], set(('perm2',)))
        self.assertEqual(pmap[1][0], Deny)
        self.assertEqual(pmap[1][1], 'role:test1')
        self.assertEqual(pmap[1][2], set(('perm1','perm2')))


class TestACLsProps(Base):

    def test_acls(self):
        import ptah

        acl1 = ptah.ACL('acl1', 'acl1')
        acl1.allow('role1', 'perm1', 'perm2')

        acl2 = ptah.ACL('acl2', 'acl2')
        acl2.deny('role1', 'perm1', 'perm2')

        class Content(object):
            __acl__ = ptah.ACLsProperty()

        content = Content()

        self.assertEqual(content.__acl__, ())

        content.__acls__ = ()
        self.assertEqual(content.__acl__, ())

        content.__acls__ = ('acl1',)
        self.assertEqual(list(content.__acl__),
                         [['Allow', 'role1', set(['perm2', 'perm1'])]])

        content.__acls__ = ('acl1', 'acl2',)
        self.assertEqual(list(content.__acl__),
                         [['Allow', 'role1', set(['perm2', 'perm1'])],
                          ['Deny', 'role1', set(['perm2', 'perm1'])]])

        content.__acls__ = ('acl2', 'acl1')
        self.assertEqual(list(content.__acl__),
                         [['Deny', 'role1', set(['perm2', 'perm1'])],
                          ['Allow', 'role1', set(['perm2', 'perm1'])]])


class TestRole(Base):

    def test_role_register(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')

        self.assertTrue(role.id == 'role:myrole')
        self.assertTrue(role.name == 'myrole')
        self.assertTrue(role.title == 'MyRole')
        self.assertTrue(role.description == '')
        self.assertTrue(str(role) == 'Role<MyRole>')
        self.assertTrue(repr(role) == 'role:myrole')

    def test_role_register_conflict(self):
        import ptah

        role1 = ptah.Role('myrole', 'MyRole1')
        role2 = ptah.Role('myrole', 'MyRole2')

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_role_roles(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')

        self.assertTrue('myrole' in ptah.Roles)
        self.assertTrue(ptah.Roles['myrole'] is role)

    def test_role_allow_permission(self):
        import ptah
        from ptah import DEFAULT_ACL

        role = ptah.Role('myrole', 'MyRole')
        role.allow('perm1', 'perm2')

        rec = DEFAULT_ACL.get(Allow, role.id)

        self.assertEqual(rec[0], Allow)
        self.assertEqual(rec[1], role.id)
        self.assertTrue('perm1' in rec[2])
        self.assertTrue('perm2' in rec[2])

    def test_role_deny_permission(self):
        import ptah
        from ptah import DEFAULT_ACL

        role = ptah.Role('myrole', 'MyRole')
        role.deny('perm1', 'perm2')

        rec = DEFAULT_ACL.get(Deny, role.id)

        self.assertEqual(rec[0], Deny)
        self.assertEqual(rec[1], role.id)
        self.assertTrue('perm1' in rec[2])
        self.assertTrue('perm2' in rec[2])

    def test_role_unset_allowed_permission(self):
        import ptah
        from ptah import DEFAULT_ACL

        role = ptah.Role('myrole', 'MyRole')
        role.allow('perm1')

        self.assertEqual(len(DEFAULT_ACL), 1)

        role.unset('perm1')
        self.assertEqual(len(DEFAULT_ACL), 0)

    def test_role_unset_denied_permission(self):
        import ptah
        from ptah import DEFAULT_ACL

        role = ptah.Role('myrole', 'MyRole')
        role.deny('perm1')

        self.assertEqual(len(DEFAULT_ACL), 1)

        role.unset('perm1')
        self.assertEqual(len(DEFAULT_ACL), 0)


class TestDefaultRoles(Base):

    def test_role_defaults(self):
        import ptah
        self._init_memphis()

        roles = list(ptah.Roles.keys())
        roles.sort()
        roles = roles[:3]

        self.assertTrue(['Authenticated', 'Everyone', 'Owner'] == roles)
        self.assertTrue(ptah.Roles['Everyone'].id == 'system.Everyone')
        self.assertTrue(ptah.Roles['Authenticated'].id=='system.Authenticated')
        self.assertTrue(ptah.Roles['Owner'].id=='system.Owner')


class Content(object):

    def __init__(self, parent=None, iface=None, acl=None):
        self.__parent__ = parent
        self.__local_roles__ = {}
        if acl is not None:
            self.__acl__ = acl

        if iface:
            interface.directlyProvides(self, iface)


class TestLocalRoles(Base):

    def test_local_role_simple(self):
        from ptah import security

        content = Content(iface=security.ILocalRolesAware)

        self.assertEqual(security.LocalRoles('userid', context=content), [])

        content.__local_roles__['userid'] = ('role:test',)

        self.assertEqual(
            security.LocalRoles('userid', context=content), ['role:test'])

    def test_local_role_lineage(self):
        from ptah import security

        parent = Content(iface=security.ILocalRolesAware)
        content = Content(parent=parent, iface=security.ILocalRolesAware)

        self.assertEqual(security.LocalRoles('userid', context=content), [])

        parent.__local_roles__['userid'] = ('role:test',)

        self.assertEqual(
            security.LocalRoles('userid', context=content), ['role:test'])

    def test_local_role_lineage_multiple(self):
        from ptah import security

        parent = Content(iface=security.ILocalRolesAware)
        content = Content(parent=parent, iface=security.ILocalRolesAware)

        self.assertEqual(security.LocalRoles('userid', context=content), [])

        parent.__local_roles__['userid'] = ('role:test',)
        content.__local_roles__['userid'] = ('role:test2',)

        lr = security.LocalRoles('userid', context=content)
        lr.sort()

        self.assertTrue(lr == ['role:test', 'role:test2'])

    def test_local_role_lineage_no_localroles(self):
        from ptah import security

        parent = Content(iface=security.ILocalRolesAware)
        content = Content(parent=parent)

        self.assertEqual(security.LocalRoles('userid', context=content), [])

        parent.__local_roles__['userid'] = ('role:test',)

        self.assertEqual(
            security.LocalRoles('userid', context=content), ['role:test'])

    def test_local_role_lineage_context_from_request(self):
        from ptah import security

        class Request(object):
            content = None
            root = None

        request = Request()

        content = Content(iface=security.ILocalRolesAware)
        content.__local_roles__['userid'] = ('role:test',)

        request.root = content

        self.assertEqual(security.LocalRoles('userid', request), ['role:test'])

        content2 = Content(iface=security.ILocalRolesAware)
        content2.__local_roles__['userid'] = ('role:test2',)

        request.context = content2
        self.assertEqual(security.LocalRoles('userid', request), ['role:test2'])


class Content2(object):

    def __init__(self, parent=None, iface=None):
        self.__parent__ = parent
        self.__owner__ = ''

        if iface:
            interface.directlyProvides(self, iface)


class TestOwnerLocalRoles(Base):

    def test_owner_role_simple(self):
        from ptah import security

        content = Content2(iface=security.IOwnersAware)

        self.assertEqual(security.LocalRoles('userid', context=content), [])

        content.__owner__ = 'userid'

        self.assertEqual(
            security.LocalRoles('userid', context=content), ['system.Owner'])

    def test_owner_role_in_parent(self):
        # return owner only on current context
        from ptah import security

        parent = Content2(iface=security.IOwnersAware)
        content = Content2(parent=parent, iface=security.IOwnersAware)

        parent.__owner__ = 'user'

        self.assertEqual(security.LocalRoles('user', context=content), [])
        self.assertEqual(
            security.LocalRoles('user', context=parent), ['system.Owner'])


class TestCheckPermission(Base):

    def setUp(self):
        super(TestCheckPermission, self).setUp()
        self._init_memphis()

    def test_checkpermission_allow(self):
        import ptah

        content = Content(acl=[DENY_ALL])

        self.assertFalse(ptah.checkPermission('View', content, throw=False))
        self.assertTrue(ptah.checkPermission(
            NO_PERMISSION_REQUIRED, content, throw=False))

    def test_checkpermission_deny(self):
        import ptah

        content = Content(acl=[(Allow, ptah.Everyone.id, ALL_PERMISSIONS)])

        self.assertTrue(ptah.checkPermission('View', content, throw=False))
        self.assertFalse(ptah.checkPermission(
            ptah.NOT_ALLOWED, content, throw=False))

    def test_checkpermission_exc(self):
        import ptah

        content = Content(acl=[DENY_ALL])

        self.assertRaises(
            HTTPForbidden, ptah.checkPermission, 'View', content, throw=True)

        content = Content(acl=[(Allow, ptah.Everyone.id, ALL_PERMISSIONS)])

        self.assertRaises(
            HTTPForbidden, ptah.checkPermission,
            ptah.NOT_ALLOWED, content, throw=True)

    def test_checkpermission_authenticated(self):
        import ptah

        content = Content(acl=[(Allow, ptah.Authenticated.id, 'View')])

        self.assertFalse(ptah.checkPermission('View', content, throw=False))

        ptah.authService.setUserId('test-user')
        self.assertTrue(ptah.checkPermission('View', content, throw=False))

    def test_checkpermission_user(self):
        import ptah

        content = Content(acl=[(Allow, 'test-user', 'View')])

        ptah.authService.setUserId('test-user')
        self.assertTrue(ptah.checkPermission('View', content, throw=False))

    def test_checkpermission_local_roles(self):
        import ptah

        content = Content(
            iface=ptah.ILocalRolesAware,
            acl=[(Allow, 'role:test', 'View')])

        ptah.authService.setUserId('test-user')
        self.assertFalse(ptah.checkPermission('View', content, throw=False))

        content.__local_roles__['test-user'] = ['role:test']
        self.assertTrue(ptah.checkPermission('View', content, throw=False))
