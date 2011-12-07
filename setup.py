import sys, os
from setuptools import setup, find_packages

version='0.2-dev'

install_requires = ['setuptools',
                    'sphinx',
                    'pytz',
                    'chameleon >= 3.6.1',
                    'pyramid >= 1.3dev',
                    'pyramid_tm',
                    'venusian', # we get it as part of pyramid
                    'zope.interface >= 3.8.0',
                    'WebOb >= 1.2b2',
                    'SQLAlchemy',
                    'SQLAHelper',
                    'Pygments',
                    'zope.sqlalchemy >= 0.7.0',
                    'transaction >= 1.2.0',
                    ]
tests_require = ['nose',
                 'pyramid_beaker',
                 'repoze.sendmail']


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
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
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
        'ptah': ['package = ptah'],
        'console_scripts': [
            'static = ptah.scripts.pstatic:main',
            'settings = ptah.scripts.settings:main',
            ],
        'paste.app_factory': [
            'app = ptah:make_wsgi_app'],
        'pyramid.scaffold': [
            'ptah101 = ptah.scaffolds:Ptah101ProjectTemplate',
            'ptah102 = ptah.scaffolds:Ptah102ProjectTemplate',
            'ptah201 = ptah.scaffolds:Ptah201ProjectTemplate',
            'ptah301 = ptah.scaffolds:Ptah301ProjectTemplate',
            ],
        },
      )
