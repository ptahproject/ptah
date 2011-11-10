Ptah Manage vs. Your App
========================

Overview
--------

By following the instructions you will end up with ptah (the library) and
scaffolding which will have generated your application.  If you goto /
you will see your application which was created by scaffolding.  If you
goto /ptah-manage/ you will see Ptah Manage.

Ptah Manage
-----------
Ptah Manage will provide introspection and management of the applications inside your system.  A goal we are striving for is to expose all of the configuration & registration inside a web ui.  We *do not* aim to support editing knobs for everything.  We *do* want to provide visibility into all registrations.

You can access Ptah Manage by going to http://localhost:8080/ptah-manage/

The default "modules" for Ptah Manage are:

  - Crowd
  
  A primitive user management module.  Your App uses crowd for its user authentication.  This UI is fairly broken at the moment.
  
  - Form fields
  
  UI listing for each ptah.form.field that is registered with Ptah.  If you create a new field and define a preview for the Field - it will show up here.  As new fields become available or you create them - you can see them here.
  
  - Introspect
  
  Ability to view registration for each package.  For a package you will be able to see Content Types, Event subscriber, Uri resolvers, Views and Routes.
  
  - Permissions
  
  Will provide listing of each permission map and what module created it.  
  
  - Ptah CMS Applications
  
  Ptah supports a concept of Applications.  Each application will be listed here and the applications' URL mount point.  
  
  - SQLAlchemy
  
  Listing of all tables being used by Ptah applications and models.  Any editing of models *will not* throw application level events.  This is provided as a convienance.
  
  - Settings
  
  Shows all values for the current running process's settings file.  Pyramid settings files are the way you manage your application configuration.  You will almost always have 2 or more settings files, one from development and one for production.  If you have configuration specific to your deployment; put the configuration in a settings file. 
  
  - Templates
  
  All templates which are registered through Ptah/Memphis will show up.  They are grouped by package in which the template is defined.  All templates are overridable.  

Ptah 301 App
------------

The Ptah301 scaffold is Your App.

Your App provides a primitive UI which provides a starting point for you to create an application.  You can see your application at /

Your App contains:

  - Actions
  
  In the left hand side you will see "actions" which the user can perform. Common actions are `Add content`, `Edit` and `Sharing`.  This is
using functionality currently inside of Ptah.  Most likely you will not
be interested in using this.
  
  - Items/Containers
  
  The first thing you see in Your App is a folder listing interface.  This is a listing of content inside the root application.  A Container can support `Rename`, `Cut`, and `Remove` actions which may be applied to its children.  You create content types and they will appear inside
of the Add Action.
  
  - Content Types
  
  Your App ships with 3 basic content types: Page, File, and Folder.  These are just implementations of `ptah.cms` models.  Create your own.  It is very easy.  And the purpose of Your App.  Customizing it.
  
  - Forms
  
  There are very basic Edit and Add forms which are used to autogenerate the forms for a model.  Again these are default implementations and do not expect them to become very sophisticated.   These forms use functionality inside of Ptah.  You can follow the forms example to create your own.
  
  - Views
  
  A set of views which will generate the layout of Your App.  Also known as the "skin", "o-wrap", "ui", "template" which puts the the pixels on the screen.  Layout's are how this is accomplished but you do not need to use layouts. 
  
  - Permissions
  
  Your App defines 3 permissions and 3 roles: `Add page`, `Add file`, and `Add folder` permissions as well as 'Viewer', 'Editor' and 'Manager' roles. It also provides an example policy of which Roles are, by default, assigned what permissions.  
  
Conclusion
----------
Ptah Manage is useful for managing configuration and providing visibility into how your application(s) are configured.  It's prime goal is to make you feel comfortable with what, how, where your application is configured.  If you do not feel comfortable with Ptah Manage - please let us know.  Asking for additional features (search for configuration variables) is out of scope.  If the information is there but you have to click around a bit -- we can fix this with UI, else let us know.

Ptah 301 scaffold is a default implementation of the `ptah.cms` and the software stack.  It is your application.  You are building a web application, right?  So here is a start.
