=================
Forms and Widgets
=================

This package provides an implementation for HTML forms and widgets. The goal
is to provide a simple API but with the ability to easily customize any data or
steps. This document, provides the content of this package's documentation
files. The documents are ordered in the way they should be read:

- ``form.txt`` [must read]

  Describes the setup and usage of forms in the most common usages. Some
  details are provided to the structure of form components.

- ``group.txt`` [must read]

  This document describes how widget groups are implemented within this
  package and how they can be used.

- ``subform.txt`` [must read]

  Introduces the complexities surrounding sub-forms and details two classes of
  sub-forms, including code examples.

- ``field.txt`` [must read]

  Provides a comprehensive explanation of the field manager API and how it is
  to be used.

- ``button.txt`` [must read]

  Provides a comprehensive explanation of the button manager API. It also
  outlines how to create buttons within schemas and how buttons are converted
  to actions.

- ``zcml.txt`` [must read]

  Explains the ZCML directives defines by this package, which are designed to
  make it easier to register new templates without writing Python code.

- ``validator.txt`` [advanced users]

  Validators are used to validate converted form data. This document provides
  a comprehensive overview of the API and how to use it effectively.

- ``widget.txt`` [advanced users]

  Explains in detail the design goals surrounding widgets and widget managers
  and how they were realized with the implemented API.

- ``contentprovider.txt`` [advanced users]

  Explains how to mix content providers in forms to render more html around
  widgets.

- ``action.txt`` [advanced users]

  Explains in detail the design goals surrounding action managers and
  actions. The execution of actions using action handlers is also covered. The
  document demonstrates how actions can be created without the use of buttons.

- ``value.txt`` [informative]

  The concept of attribute value adapters is introduced and fully
  explained. Some motivation for this new and powerful pattern is given as
  well.

- ``datamanager.txt`` [informative]

  Data managers are resposnsible for accessing and writing the data. While
  attribute access is the most common case, data managers can also manage
  other data structures, such as dictionaries.

- ``converter.txt`` [informative]

  Data converters convert data between internal and widget values and vice
  versa.

- ``term.txt`` [informative]

  Terms are wrappers around sources and vocabularies to provide a common
  interface for choices in this package.

- ``util.txt`` [informative]

  The ``util`` module provides several helper functions and classes. The
  components not tested otherwise are explained in this file.

- ``adding.txt`` [informative]

  This module provides a base class for add forms that work with the
  ``IAdding`` interface.

- ``testing.txt`` [informative]

  The ``testing`` module provides helper functions that make it easier to tet
  form-based code in unit tests. It also provides components that simplify
  testing in testbrowser and Selenium.

- ``object-caveat.txt`` [informative]

  Explains the current problems of ObjectWidget.


Browser Documentation
---------------------

There are several documentation files in the ``browser/`` sub-package. They
mainly document the basic widgets provided by the package.

- ``README.txt`` [advanced users]

  This file contains a checklist, ensuring that all fields have a widget.

- ``<fieldname>.txt``

  Each field name documentation file comprehensively explains the widget and
  how it is ensured to work properly.
