""" static assets """
from ptah import view

view.static('jquery', 'ptah:static/jquery')
view.static('bootstrap', 'ptah:static/bootstrap')
view.static('tiny_mce', 'ptah:static/tiny_mce')

# jQuery library
view.library(
    'jquery',
    path="jquery-1.6.4.min.js",
    resource="jquery",
    type="js")

view.library(
    'jquery-ui',
    path="jquery-ui-1.8.16.min.js",
    type="js",
    resource="jquery",
    require="jquery")

view.library(
    'jquery-ui',
    path="jquery-ui.css",
    resource="jquery",
    type='css')

# Bootstrap css
view.library(
    'bootstrap',
    path="bootstrap-1.3.0.min.css",
    resource="bootstrap",
    type="css")

view.library(
    'bootstrap-js',
    path="bootstrap-1.3.0.js",
    resource="bootstrap",
    type="js",
    require="jquery")

# TinyMCE
view.library(
    "tiny_mce",
    resource="tiny_mce",
    path=('tiny_mce.js', 'jquery.tinymce.js'),
    type="js",
    require='jquery')
