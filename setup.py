""" Setup for memphis package """
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version='1.0dev'

setup(name='memphis',
      version=version,
      description="",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='https://github.com/ptahproject/memphis/',
      license='BSD-derived',
      packages = find_packages(),
      install_requires = ['setuptools',
                          'colander',
                          'iso8601',
                          'chameleon',
                          'pyramid',
                          'pytz',
                          'simplejson',
                          'zope.interface >= 3.8.0',
                          ],
      include_package_data = True,
      zip_safe = False,
      entry_points = {
        'memphis': ['package = memphis'],
        'console_scripts': [
            'settings = memphis.config.commands:settingsCommand',
            ],
        'paste.global_paster_command': [
            'static = memphis.view.commands:StaticCommand',
            'templates = memphis.view.commands:TemplatesCommand',
            ],
        },
      )
