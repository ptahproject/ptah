Ptah settings
-------------
All .INI settings set in file are in JSON format. All examples in this document are given in JSON format.  An example entry in .ini file::

  [app:ptah]
  ptah.managers = ["*"]
  ptah.pwd_manager = "ssha"

All values passed inside of Pyramid configurator are in Python format::

  config.ptah_init_manage(
      managers = ['*'],
      disable_modules = ['rest', 'introspect', 'apps', 'permissions'])
  
``ptah.disable_modules``

  Hide Modules in Management UI. List of modules names to hide in manage ui. e.g.::
  
    ptah.disable_modules = ["rest", "apps"]

``ptah.enable_modules``

  Enable Modules in Management UI. List of modules names to enable in 
  manage ui. e.g.::
  
    ptah.enable_modules = ["rest", "apps"]

``ptah.disable_models``

  Provides a mechanism to hide models in the Model Management UI.  A list of models to hide in model manage ui. e.g.::
  
    ptah.disable_models = ["link"]

``ptah.email_from_name``

  Site admin name. Default is ``Site administrator``. e.g.::
  
    ptah.email_from_name = "Site Administrator"

``ptah.email_from_address``

  Site admin email address. e.g.::
  
    ptah.email_from_address = "no-reply@myapplication.com"

``ptah.manage``

  Ptah manage id. Default value is ``ptah-manage``. Also this value is being 
  used for ptah management url `http://localhost:6543/ptah-manage/...` e.g.::
  
    ptah.manage = "manage"

  The Ptah Manage UI would then be available at `http://localhost:6543/manage`

``ptah.manager_role``

  Specific role with access rights to ptah management ui.

``ptah.managers``

  List of user logins with access rights to ptah management ui.  Default value is empty string, '' which means no one logins allowed.  "*" allows all principals.  Must be a list of strings, e.g.::
  
    ptah.managers = ["userid"]

``ptah.pwd_manager``

  Password manager (plain, ssha, ..)

``ptah.pwd_min_length``

  Minimum length for password.  

``ptah.pwd_letters_digits``

  Use letters and digits in password. Boolean value.

``ptah.pwd_letters_mixed_case``

  Use letters in mixed case.  Boolean value.

``ptah.secret``

  Authentication policy secret. The secret (a string) used for 
  auth_tkt cookie signing.  e.g.::
  
      ptah.secret = "s3cr3t"

``ptah.db_skip_tables``

  Do not create listed tables during data population process. e.g.::
  
      ptah.db_skip_tables = ["ptah_nodes", "ptah_content"]

``ptah.default_roles``

  List of default principal roles::
  
      ptah.default_roles = ["role:Editor"]
