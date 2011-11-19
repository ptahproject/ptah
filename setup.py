import sys, os
from setuptools import setup, find_packages

version='0.1'

install_requires = ['setuptools',
                    'sphinx',
                    'colander >= 0.9.4',
                    'pytz',
                    'iso8601',
                    'simplejson',
                    'chameleon == 2.4.5',
                    'pyramid',
                    'pyramid_tm',
                    'zope.interface >= 3.8.0',
                    'WebOb >= 1.2b2',
                    'SQLAlchemy',
                    'SQLAHelper',
                    'Pygments',
                    ]
tests_require = ['nose']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(name='ptah',
      version=version,
      description=('Ptah is a fast, fun, open source high-level '
                   'Python web development environment.'),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          'Framework :: Pylons',
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
            'ptah101 = ptah.scaffolds:Ptah101ProjectTemplate',
            'ptah102 = ptah.scaffolds:Ptah102ProjectTemplate',
            'ptah201 = ptah.scaffolds:Ptah201ProjectTemplate',
            'ptah301 = ptah.scaffolds:Ptah301ProjectTemplate',
            ],
        'paste.global_paster_command': [
            'static = ptah.view.commands:StaticCommand',
            ],
        },
      )
