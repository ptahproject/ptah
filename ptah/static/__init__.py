""" assets libraries """
import ptah

# jQuery library
ptah.library(
    'jquery',
    path='ptah:static/jquery/jquery-1.7.1.min.js',
    type="js")

ptah.library(
    'jquery-ui',
    path='ptah:static/jquery/jquery-ui-1.8.17.min.js',
    type="js",
    require="jquery")

ptah.library(
    'jquery-ui',
    'ptah:static/jquery/jquery-ui-1.8.17.css',
    type='css')

# Bootstrap css
ptah.library(
    'bootstrap',
    path='ptah:static/bootstrap/bootstrap-2.0.0.min.css',
    type="css")

ptah.library(
    'bootstrap-js',
    path='ptah:static/bootstrap/bootstrap-2.0.0.min.js',
    type="js",
    require="jquery")

# TinyMCE
ptah.library(
    "tiny_mce",
    path='ptah:static/tiny_mce/tiny_mce.js',
    type="js",
    require='jquery')
