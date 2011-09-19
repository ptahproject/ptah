""" role """
from memphis import config

from base import Base


class Role(Base):

    def test_role_register(self):
        import ptah

        role = ptah.registerRole('myrole', 'MyRole')
        
        self.assertTrue(role.id == 'role:myrole')
        self.assertTrue(role.name == 'myrole')
        self.assertTrue(role.title == 'MyRole')
        self.assertTrue(role.description == '')

    def test_role_register_conflict(self):
        import ptah

        role1 = ptah.registerRole('myrole', 'MyRole1')
        role2 = ptah.registerRole('myrole', 'MyRole2')
        
        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_role_roles(self):
        import ptah

        role = ptah.registerRole('myrole', 'MyRole')

        self.assertTrue('myrole' in ptah.Roles)
        self.assertTrue(ptah.Roles['myrole'] is role)
