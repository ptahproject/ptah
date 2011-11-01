import sys, os
from setuptools import setup, find_packages

version='0.1'

install_requires = ['setuptools',
                    'docutils',
                    'colander >= 0.9.4',
                    'pytz',
                    'iso8601',
                    'simplejson',
                    'chameleon == 2.4.5',
                    'pyramid',
                    'pyramid_tm',
                    'pyramid_beaker',
                    'repoze.sendmail',
                    'zope.interface >= 3.8.0',
                    'WebOb >= 1.2b2',
                    'SQLAlchemy',
                    'SQLAHelper',
                    'Pygments',
                    ]
tests_require = ['nose']

if sys.platform == 'linux2':
    tests_require.append('pyinotify')


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
      install_requires = install_requires,
      tests_require = tests_require,
      test_suite = 'nose.collector',
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'ptah': ['package = ptah'],
        'console_scripts': [
            'settings = ptah.config.commands:settingsCommand',
            ],
        'paste.app_factory': [
            'app = ptah:make_wsgi_app'],
        'paste.paster_create_template': [
            'ptahdemo = ptah.scaffolds:StarterProjectTemplate',
            ],
        'paste.global_paster_command': [
            'static = ptah.view.commands:StaticCommand',
            'templates = ptah.view.commands:TemplatesCommand',
            ],
        },
      )
