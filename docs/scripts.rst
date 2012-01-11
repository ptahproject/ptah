.. _command_line_chapter:

Command-line utilities
======================

Your ptah application can be controlled and inspected using a variety 
of command-line utilities. These utilities are documented in this chapter.


Application Settings
--------------------

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


Application Information
-----------------------

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


.. _data_populate_script:

Data population
---------------

You can use the ``ptah-populate`` command in a terminal window to execute a 
populate steps registered with :py:func:`ptah.populate` api. Much like 
the any pyramid command, the ``ptah-populate`` command accepts one argument 
with the format ``config_file#section_name``.

Use ``-l`` argument to list all registered steps.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-populate development.ini -l

   * ptah-db-schema: Create db schema (active)

   * ptah-crowd-admin: Create admin user (active)

   ...

It shows step name, then step title, and activity state. If step is active
it is beeing executed automatically with ``-a`` argument.

Use ``-a`` argument to execute all active steps.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-populate development.ini -a
   2012-01-03 12:43:46,796 INFO  [ptah][MainThread] Executing populate step: ptah-db-schema
   2012-01-03 12:43:46,797 INFO  [ptah][MainThread] Creating db table `ptah_crowd`.
   2012-01-03 12:43:46,931 INFO  [ptah][MainThread] Creating db table `ptah_blobs`
   ...
   2012-01-03 12:43:48,087 INFO  [ptah][MainThread] Executing populate step: ptah-crowd-admin
   2012-01-03 12:43:48,092 INFO  [ptah_crowd][MainThread] Creating admin user `admin` Ptah admin
   ...


Its possible to execute `inactive` steps or specific step with all required
steps. Specify step names in command line after your ini file.

.. code-block:: text
   :linenos:

   [fafhrd@... MyProject]$ ../bin/ptah-populate development.ini ptah-db-schema ptah-crowd-admin


.. _data_migration_script:

Data migration
--------------

You can use the ``ptah-migrate`` command in a terminal window to execute a 
migration steps registered with :py:func:`ptah.register_migration` api. 
Much like  the any pyramid command, the ``ptah-migrate`` command accepts 
first argument with the format ``config_file#section_name``.

Use ``list`` argument to list all registered migrations.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-migrate development.ini list

   * ptah: Ptah database migration
       ptah:migrations
       /...src/ptah/ptah/migrations

   ...


Use ``revision`` argument to create new revision for registered migration.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-migrate development.ini revision ptah
     Generating /../src/ptah/ptah/migrations/3fd73c8b8727.py...done
   ...

Additional arguments:

  ``-r`` specify custom revision id. revision id has to contain only 
  letters and numbers.

  ``-m`` specify revision message

Full command can look like:

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-migrate development.ini revision ptah -r 001 -m "Add new column X"
     ...


Use ``upgrade`` argument to upgrade package to specific revision. You can 
specify one or more packages after ``upgrade`` argument.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-migrate development.ini upgrade ptah
   2012-01-11 17:00:44,506 INFO  [ptah.alembic] ptah: running upgrade None -> 0301
   ...

To specify specific revision number use ``:`` and revision number. For example
``ptah:0301``


Use ``current`` argument to check current package revision. You can
specify any number of package after ``current`` argument. If package is not 
specified script shows information for all packages.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-migrate development.ini current ptah
   Package 'ptah' rev: 0301(head) Migration to ptah 0.3


Use ``history`` argument to check migrations history.

.. code-block:: text
   :linenos:
   
   [fafhrd@... MyProject]$ ../bin/ptah-migrate development.ini history ptah

   ptah
   ====
   0301: Ptah 0.3.0 changes
