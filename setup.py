import sys, os
from setuptools import setup, find_packages

version='0.1dev'

setup(name='ptah_cms',
      version=version,
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/ptah_cms/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      install_requires = ['setuptools',
                          'ptah',
                          'sqlalchemy',
                          'pyramid_sqla',
                          'memphis.view',
                          'memphis.config',
                          'memphis.form',
                          'zope.component',
                          'zope.interface',
                          ],
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['package = ptah_cms']
        }
      )
