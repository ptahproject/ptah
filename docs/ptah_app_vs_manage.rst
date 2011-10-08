Ptah Manage vs. Ptah App
========================

The UI isnt great right now.  We currently use twitter bootstrap.  If you are a UI person and interested in helping - please create issue in github.

Overview
--------

By installing ptah you get 2 applications which have UI.  One is called "ptah-manage" or the Management UI and the other is the "ptah-app".  Ptah App is the default implementaiton of the CMS.  It is a default implementation of the Ptah CMS.  We are currently using Ptah App to prototype and it will be unstable for awhile.  Ptah Manage is fairly stable and existed long before Ptah App.

Ptah Manage
-----------
Ptah Manage will provide introspection and management of the applications inside your system.  A goal we are striving for is to expose all of the configuration & registration inside a web ui.  We *do not* aim to support editing knobs for everything.  We *do* want to provide visibility into all registrations.

You can access Ptah Manage by going to http://localhost:8080/ptah-manage/

The default "modules" for Ptah Manage are:

  - Crowd
  
  A primitive user management module.  Ptah App uses crowd for its user authentication.  This UI is fairly broken at the moment.
  
  - Form fields
  
  UI listing for each memphis.form.field that is registered with Ptah.  If you create a new field and define a preview for the Field - it will show up here.  As new fields become available or you create them - you can see them here.
  
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

Ptah App
--------

The Ptah App is a default UI to see how the basic functionality works.  It supports a Page/Folder paradigm but we recommend against that paradigm unless you are absolutely required to support it.  This UI will become more sophisticated and will be the "Demo application" for Ptah usage.  It is experimental but is meant to demonstrate the features of Ptah.

You can see the Ptah App by going to http://localhost:8080/ and you can login by going to http://localhost:8080/login.html 

The current features for Ptah App:

  - Actions
  
  In the left hand side you will see "actions" which the user can perform. Common actions are `Add content`, `Edit` and `Sharing`.  
  
  - Websocket
  
  If you are using the socket-server provided then you should get `growl` like notifications when application or content-level events are thrown. 
  
  - Items/Containers
  
  The first thing you see in Ptah App is a folder listing interface.  This is a listing of content inside the root application.  A Container can support `Rename`, `Cut`, and `Remove` actions which may be applied to its children.
  
  - Content Types
  
  Ptah App ships with 3 basic content types: Page, File, and Folder.  These are just implementations of `ptah_cms` models.
  
  - TinyMCE field
  
  There is a primitive TinyMCE field which is included in Ptah App which is used by Page model.  
  
  - Forms
  
  There are very basic Edit and Add forms which are used to autogenerate the forms for a model.  Again these are default implementations and do not expect them to become very sophisticated.  
  
  - Views
  
  A set of views which will generate the layout of the Ptah App.  Also known as the "skin", "o-wrap", "ui", "template" which puts the the pixels on the screen. 
  
  - Permissions
  
  Ptah App defines 3 permissions: `Add page`, `Add file`, and `Add folder`. It also provides an example policy of which Roles are, by default, assigned what permissions.  
  
Conclusion
----------
Ptah Manage is useful for managing configuration and providing visibility into how your application(s) are configured.  It's prime goal is to make you feel comfortable with what, how, where your application is configured.  If you do not feel comfortable with Ptah Manage - please let us know.  Asking for additional features (search for configuration variables) is out of scope.  If the information is there but you have to click around a bit -- we can fix this with UI, else let us know.

Ptah App is a default implementation of the `ptah_cms` and the software stack.  While some people may want to extend it - it's job in life is not to support being an Enterprise Content Management System.  It's job is to demonstrate the Ptah CMS stack and a reference implementation of those features.
