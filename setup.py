import os
import sys
import logging
import multiprocessing # atexit exception
from setuptools import setup, find_packages

version='0.3.2'

install_requires = ['setuptools',
                    'alembic',
                    'chameleon >= 2.6.1',
                    'pyramid >= 1.3a5',
                    'pyramid_tm',
                    'zope.interface >= 3.8.0',
                    'zope.sqlalchemy >= 0.7.0',
                    'transaction >= 1.2.0',
                    'venusian',
                    'WebOb >= 1.2b2',
                    'SQLAlchemy',
                    'Pygments',
                    'pytz',
                    'sphinx',
                    ]

if sys.version_info[:2] == (2, 6):
    install_requires.extend((
            'argparse',
            'ordereddict',
            'unittest2'))

tests_require = install_requires + ['nose']

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(name='ptah',
      version=version,
      description=('Ptah is a fast, fun, open source high-level '
                   'Python web development environment.'),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: Implementation :: CPython",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
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
          'console_scripts': [
              'ptah-manage = ptah.scripts.manage:main',
              'ptah-migrate = ptah.scripts.migrate:main',
              'ptah-populate = ptah.scripts.populate:main',
              'ptah-settings = ptah.scripts.settings:main',
              ],
          'pyramid.scaffold': [
              'ptah_starter = ptah.scaffolds:PtahStarterProjectTemplate',
              ],
          },
      package_data = {'migrations': ['ptah/migrations/*.py']},
      )
