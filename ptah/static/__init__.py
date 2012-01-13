""" assets libraries """
import ptah

# jQuery library
ptah.library(
    'jquery',
    path='ptah:static/jquery/jquery-1.7.min.js',
    type="js")

ptah.library(
    'jquery-ui',
    path='ptah:static/jquery/jquery-ui-1.8.16.min.js',
    type="js",
    require="jquery")

ptah.library(
    'jquery-ui',
    'ptah:static/jquery/jquery-ui.css',
    type='css')

# Bootstrap css
ptah.library(
    'bootstrap',
    path='ptah:static/bootstrap/bootstrap-1.4.0.min.css',
    type="css")

ptah.library(
    'bootstrap-js',
    path=('ptah:static/bootstrap/js/bootstrap-alerts.js',
          'ptah:static/bootstrap/js/bootstrap-buttons.js',
          'ptah:static/bootstrap/js/bootstrap-dropdown.js',
          'ptah:static/bootstrap/js/bootstrap-modal.js',
          'ptah:static/bootstrap/js/bootstrap-scrollspy.js',
          'ptah:static/bootstrap/js/bootstrap-tabs.js',
          'ptah:static/bootstrap/js/bootstrap-twipsy.js',
          'ptah:static/bootstrap/js/bootstrap-popover.js'),
    type="js",
    require="jquery")

# TinyMCE
ptah.library(
    "tiny_mce",
    path=('ptah:static/tiny_mce/tiny_mce.js',
          'ptah:static/tiny_mce/jquery.tinymce.js'),
    type="js",
    require='jquery')
