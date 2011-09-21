""" role """
from zope import interface
from memphis import config
from pyramid.security import ALL_PERMISSIONS

from base import Base


class Role(Base):

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

        role = ptah.Role('myrole', 'MyRole')

        role.allow('perm1', 'perm2')

        self.assertTrue('perm1' in role.allowed)
        self.assertTrue('perm2' in role.allowed)

        role.allow('perm1')

        perms = list(role.allowed)
        perms.sort()
        self.assertTrue(['perm1','perm2'] == perms)

    def test_role_allow_all_permission(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')
        role.allow('perm1')

        role.allow(ALL_PERMISSIONS)
        self.assertTrue(role.allowed is ALL_PERMISSIONS)
        self.assertTrue('perms1' in role.allowed)

        role.allow('perm1')
        self.assertTrue(role.allowed is ALL_PERMISSIONS)

    def test_role_deny_permission(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')

        role.deny('perm1', 'perm2')

        self.assertTrue('perm1' in role.denied)
        self.assertTrue('perm2' in role.denied)

        role.deny('perm1')

        perms = list(role.denied)
        perms.sort()
        self.assertTrue(['perm1','perm2'] == perms)

    def test_role_deny_all_permission(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')
        role.deny('perm1')

        role.deny(ALL_PERMISSIONS)
        self.assertTrue(role.denied is ALL_PERMISSIONS)
        self.assertTrue('perms1' in role.denied)

        role.deny('perm1')
        self.assertTrue(role.denied is ALL_PERMISSIONS)

    def test_role_unset_allowed_permission(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')
        role.allow('perm1')

        self.assertTrue(('perm1',) == tuple(role.allowed))
        
        role.unset('perm1')
        self.assertTrue(() == tuple(role.allowed))

    def test_role_unset_allowed_all_permission(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')
        role.allow('perm1')
        self.assertTrue(('perm1',) == tuple(role.allowed))
        
        role.unset(ALL_PERMISSIONS)
        self.assertTrue(() == tuple(role.allowed))

        role.allow(ALL_PERMISSIONS)
        role.unset(ALL_PERMISSIONS)
        self.assertTrue(() == tuple(role.allowed))

    def test_role_unset_denied_permission(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')
        role.deny('perm1')

        self.assertTrue(('perm1',) == tuple(role.denied))
        
        role.unset('perm1')
        self.assertTrue(() == tuple(role.denied))

    def test_role_unset_denied_all_permission(self):
        import ptah

        role = ptah.Role('myrole', 'MyRole')
        role.deny('perm1')
        self.assertTrue(('perm1',) == tuple(role.denied))
        
        role.unset(ALL_PERMISSIONS)
        self.assertTrue(() == tuple(role.denied))

        role.deny(ALL_PERMISSIONS)
        role.unset(ALL_PERMISSIONS)
        self.assertTrue(() == tuple(role.denied))


class DefaultRoles(Base):

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

    def __init__(self, parent=None, iface=None):
        self.__parent__ = parent
        self.__local_roles__ = {}

        if iface:
            interface.directlyProvides(self, iface)


class LocalRoles(Base):

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
        self.__owners__ = {}

        if iface:
            interface.directlyProvides(self, iface)


class OwnerLocalRoles(Base):

    def test_owner_role_simple(self):
        from ptah import security

        content = Content2(iface=security.IOwnersAware)

        self.assertEqual(security.LocalRoles('userid', context=content), [])

        content.__owners__ = ['userid']

        self.assertEqual(
            security.LocalRoles('userid', context=content), ['system.Owner'])

    def test_owner_role_multple(self):
        from ptah import security

        content = Content2(iface=security.IOwnersAware)

        content.__owners__ = ['user1', 'user2']

        self.assertEqual(
            security.LocalRoles('user1', context=content), ['system.Owner'])

        self.assertEqual(
            security.LocalRoles('user2', context=content), ['system.Owner'])

    def test_owner_role_in_parent(self):
        # return owner only on current context
        from ptah import security

        parent = Content2(iface=security.IOwnersAware)
        content = Content2(parent=parent, iface=security.IOwnersAware)

        parent.__owners__ = ['user']

        self.assertEqual(security.LocalRoles('user', context=content), [])
        self.assertEqual(
            security.LocalRoles('user', context=parent), ['system.Owner'])


class DefaultACL(Base):

    def test_default_acl(self):
        from ptah import security

        self.assertEqual(security.ACL, [])
        
        role = security.Role('myrole', 'MyRole')

        role.allow('perm1', 'perm2')
        role.deny('perm1')

        self._init_memphis()

        self.assertEqual(security.ACL[0],
                         ('Deny', 'role:myrole', set(['perm1'])))
        self.assertEqual(security.ACL[1],
                         ('Allow', 'role:myrole', set(['perm1', 'perm2'])))
