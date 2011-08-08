""" Setup for memphis.view package """
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0.9dev'

setup(name='memphis.view',
      version=version,
      description="A package implementing advanced Page Template patterns.",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('memphis', 'view', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Repoze Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/memphis.view/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      namespace_packages=['memphis'],
      install_requires = ['setuptools',
                          'webob',
                          'chameleon>=2.0-rc11',
                          'zope.component',
                          'zope.interface',
                          'zope.i18n',
                          'memphis.config >= 0.6',
                          'simplejson',
                          ],
      extras_require = dict(
        test=['memphis.config [test]',
              'pyramid',
              'zope.publisher',
              'Zope2',
              'AccessControl',
              'Products.statusmessages',
              ],
        pyramid=['pyramid'],
        zope=['AccessControl',
              'Products.statusmessages',
              'zope.publisher']
        ),
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['grokker = memphis.view.meta',
                    'package = memphis.view']
        }
      )
