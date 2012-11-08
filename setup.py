import os
import sys
from setuptools import setup, find_packages

version = '0.8.0'

install_requires = ['setuptools',
                    'alembic >= 0.4.0',
                    'Chameleon >= 2.6.1',
                    'pyramid >= 1.4a2',
                    'pyramid_tm',
                    'pyramid_amdjs',
                    'pform',
                    'player',
                    'zope.interface >= 4.0.1',
                    'zope.sqlalchemy >= 0.7.1',
                    'transaction >= 1.3.0',
                    'venusian >= 1.0a6',
                    'WebOb >= 1.2',
                    'SQLAlchemy >= 0.7.2',
                    'pytz',
                    ]

if sys.version_info[:2] == (2, 6):
    install_requires.extend((
            'argparse',
            'ordereddict',
            'unittest2'))

if sys.version_info[:2] in ((2,6),(2,7)):
    install_requires.extend(('simplejson',))

tests_require = install_requires + ['nose', 'mock', 'sphinx', 'Pygments']


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
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: Implementation :: CPython",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Ptah Project',
      author_email='ptahproject@googlegroups.com',
      url='https://github.com/ptahproject/ptah/',
      license='BSD-derived',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require = dict(test=tests_require),
      tests_require=tests_require,
      test_suite='nose.collector',
      include_package_data=True,
      zip_safe=False,
      entry_points={
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
      message_extractors={'ptah': [
          ('scaffolds/**', 'ignore', None),
          ('scripts/**', 'ignore', None),
          ('static/**', 'ignore', None),
          ('tests/**', 'ignore', None),
          ('*/tests/**', 'ignore', None),
          ('**.py', 'lingua_python', None),
          ('**.pt', 'lingua_xml', None),
          ('**.mustache', 'mustache', None),
          ('**.hb', 'mustache', None),
          ]},
      )
