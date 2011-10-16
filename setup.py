import sys, os
from setuptools import setup, find_packages

version='0.1'

setup(name='ptah',
      version=version,
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Ptah Project',
      author_email='ptahproject@googlegroups.com',
      url='https://github.com/ptahproject/ptah/',
      license='BSD-derived',
      packages=find_packages(),
      install_requires = ['setuptools',
                          'memphis',
                          'pyramid_tm',
                          'pyramid_beaker',
                          'zope.interface',
                          'repoze.sendmail',
                          'SQLAlchemy',
                          'SQLAHelper',
                          'Pygments',
                          ],
      tests_require = ['nose'],
      test_suite = 'nose.collector',
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['package = ptah'],
        'paste.app_factory': [
            'app = ptah:make_wsgi_app'],
        'paste.paster_create_template': [
            'ptahdemo = ptah_app.scaffolds:StarterProjectTemplate',
            ]
        },
      )
