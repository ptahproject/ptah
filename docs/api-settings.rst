Ptah settings
-------------
All settings can be set in INI file. Settings values are in json format::

  [app:ptah]
  ptah.managers = ["*"]
  ptah.pwd_manager = "ssha"

ptah.secret

  Authentication policy secret. The secret (a string) used for 
  auth_tkt cookie signing

ptah.settings_dbpoll

  Settings db poll interval (seconds). If you allow to change setting ttw.
  "0" means do not poll

ptah.manage

  Ptah manage id. Default value is ``ptah-manage``. Also this value is beein 
  used for ptah management url `http://localhost:6543/ptah-manage/...`

ptah.managers

  List of user logins with access rights to ptah management ui.

ptah.manager_role

  Specific role with access rights to ptah management ui.

ptah.disable_modules

  Hide Modules in Management UI. List of modules names to hide in manage ui

ptah.disable_models

  Hide Models in Model Management UI. List of models to hide in model manage ui.

ptah.email_from_name

  Site admin name. Default is ``Site administrator``

ptah.email_from_address

  Site admin email address.

ptah.pwd_manager

  Password manager (plain, ssha, ..)

ptah.pwd_min_length

  Minimum length for password.

ptah.pwd_letters_digits

  Use letters and digits in password.

ptah.pwd_letters_mixed_case

  Use letters in mixed case.
