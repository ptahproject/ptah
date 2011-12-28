.. _command_line_chapter:

Command-line utilities
======================

Your ptah application can be controlled and inspected using a variety 
of command-line utilities. These utilities are documented in this chapter.


Displaying Application Settings
-------------------------------

You can use the ``ptah-settings`` command in a terminal window to print a 
summary of settings to your application registered with 
:py:func:`ptah.register_settings` api. Much like the any pyramid 
command, the ``ptah-settings`` command accepts one argument with the
format ``config_file#section_name``. The
``config_file`` is the path to your application's ``.ini`` file, and
``section_name`` is the ``app`` section name inside the ``.ini`` file which
points to your application.  By default, the ``section_name`` is ``main`` and
can be omitted.

For example:
    
.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-settings development.ini

   * Ptah settings (ptah)

     - ptah.secret: Authentication policy secret (TextField: secret-
       ptah!)
          The secret (a string) used for auth_tkt cookie signing

     - ptah.manage: Ptah manage id (TextField: ptah-manage)

   ...

By default ``ptah-settings`` shows all sections. It possible to show
only certain settings section like "ptah" or "format". 

It is possible to print all settings in ``.ini`` format. 

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-settings development.ini -p
   [DEFAULT]
   format.date_full = "%%A, %%B %%d, %%Y"
   format.date_long = "%%B %%d, %%Y"
   format.date_medium = "%%b %%d, %%Y"
   format.date_short = "%%m/%%d/%%y"
   format.time_full = "%%I:%%M:%%S %%p %%Z"
   format.time_long = "%%I:%%M %%p %%z"
   format.time_medium = "%%I:%%M %%p"
   format.time_short = "%%I:%%M %%p"
   format.timezone = "us/central"
   ptah.disable_models = []
   ptah.disable_modules = []
   ...
   ptah.pwd_letters_digits = false
   ptah.pwd_letters_mixed_case = false
   ptah.pwd_manager = "plain"
   ptah.pwd_min_length = 5


Displaying Various Application Information
------------------------------------------

You can use the ``ptah-manage`` command in a terminal window to print a 
summary of different information of your application. The ``ptah-manage`` 
command accepts one argument with the format ``config_file#section_name``.

List management modules
~~~~~~~~~~~~~~~~~~~~~~~

Use ``--list-modules`` argument to the ``ptah-manage`` to list all
registered ptah management modules.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-manage development.ini --list-modules

   * apps: Applications (disabled: False)
       A listing of all registered Ptah Applications.

   * crowd: User management (disabled: False)
       Default user management. Create, edit, and activate users.

   * fields: Field types (disabled: False)
       A preview and listing of all form fields in the application. This
       is useful to see what fields are available. You may also interact
       with the field to see how it works in display mode.

   ...


List db models
~~~~~~~~~~~~~~

Use ``--list-models`` argument to the ``ptah-manage`` to list all
registered ptah models.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-manage development.ini --list-models

   * cms-type:app: Application (disabled: False)
       Default ptah application

       class: ApplicationRoot
       module: MyProject.root
       file:  .../root.pyc

   ...

