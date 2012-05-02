""" assets libraries """
import ptah

# jQuery library
ptah.library(
    'jquery',
    path='ptah:static/jquery/jquery-1.7.2.min.js',
    type="js")

ptah.library(
    'jquery-ui',
    path='ptah:static/jquery/jquery-ui-1.8.20.min.js',
    type="js",
    require="jquery")

ptah.library(
    'jquery-ui',
    'ptah:static/jquery/jquery-ui-1.8.20.css',
    type='css')

# Bootstrap css
ptah.library(
    'bootstrap',
    path='ptah:static/bootstrap/bootstrap.min.css',
    type="css")

ptah.library(
    'bootstrap-js',
    path='ptah:static/bootstrap/bootstrap.min.js',
    type="js",
    require="jquery")

# CKEditor
ptah.library(
    'ckeditor',
    path='ptah:static/ckeditor/ckeditor.js',
    type="js",
    require="jquery")
