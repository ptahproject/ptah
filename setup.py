import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0.4'

setup(name='memphis.form',
      version=version,
      description="Fork of z3c.form library.",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('memphis', 'form', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/memphis.form/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      namespace_packages=['memphis'],
      install_requires = ['setuptools',
                          'chameleon',
                          'memphis.view',
                          'memphis.config',
                          'zope.event',
                          'zope.schema',
                          'zope.component',
                          'zope.interface',
                          'zope.configuration',
                          'zope.contenttype',
                          'zope.lifecycleevent',
                          ],
      extras_require = dict(
          test=['lxml',
                'pyramid',
                'memphis.view [test]',]),
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['package = memphis.form']
        }
      )
