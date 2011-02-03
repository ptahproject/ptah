##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bootstrap a buildout-based project

Simply run this script in a directory containing a buildout.cfg.
The script accepts buildout command-line options, so you can
use the -c option to specify an alternate configuration file.
"""

import os
import shutil
import sys
import tempfile
import urllib2
from optparse import OptionParser

tmpeggs = tempfile.mkdtemp()

is_jython = sys.platform.startswith('java')

# parsing arguments
parser = OptionParser()
parser.add_option("-v", "--version", dest="version",
                          help="use a specific zc.buildout version")
parser.add_option("-d", "--distribute",
                   action="store_true", dest="distribute", default=False,
                   help="Use Disribute rather than Setuptools.")

parser.add_option("-c", None, action="store", dest="config_file",
                   help=("Specify the path to the buildout configuration "
                         "file to be used."))

options, args = parser.parse_args()

# if -c was provided, we push it back into args for buildout' main function
if options.config_file is not None:
    args += ['-c', options.config_file]

if options.version is not None:
    VERSION = '==%s' % options.version
else:
    VERSION = ''

# We decided to always use distribute, make sure this is the default for us
# USE_DISTRIBUTE = options.distribute
USE_DISTRIBUTE = True
args = args + ['bootstrap']

to_reload = False
try:
    import pkg_resources
    if not hasattr(pkg_resources, '_distribute'):
        to_reload = True
        raise ImportError
except ImportError:
    ez = {}
    if USE_DISTRIBUTE:
        setup_url = 'http://python-distribute.org/distribute_setup.py'
        exec urllib2.urlopen(setup_url).read() in ez
        ez['use_setuptools'](to_dir=tmpeggs, download_delay=0, no_fake=True)
    else:
        ez_setup_url = 'http://peak.telecommunity.com/dist/ez_setup.py'
        exec urllib2.urlopen(ez_setup_url).read() in ez
        ez['use_setuptools'](to_dir=tmpeggs, download_delay=0)

    if to_reload:
        reload(pkg_resources)
    else:
        import pkg_resources


def quote(c):
    if sys.platform == 'win32':
        if ' ' in c:
            return '"%s"' % c  # work around spawn lamosity on windows
    return c

cmd = 'from setuptools.command.easy_install import main; main()'
ws = pkg_resources.working_set

if USE_DISTRIBUTE:
    requirement = 'distribute'
else:
    requirement = 'setuptools'

pythonpath = ws.find(pkg_resources.Requirement.parse(requirement)).location

if is_jython:
    import subprocess

    assert subprocess.Popen([sys.executable] + ['-c', quote(cmd), '-mqNxd',
           quote(tmpeggs), 'zc.buildout' + VERSION],
           env=dict(os.environ,
               PYTHONPATH=pythonpath),
           ).wait() == 0

else:
    assert os.spawnle(
        os.P_WAIT, sys.executable, quote(sys.executable),
        '-c', quote(cmd), '-mqNxd', quote(tmpeggs), 'zc.buildout' + VERSION,
        dict(os.environ,
            PYTHONPATH=pythonpath),
        ) == 0

ws.add_entry(tmpeggs)
ws.require('zc.buildout' + VERSION)
import zc.buildout.buildout
zc.buildout.buildout.main(args)
shutil.rmtree(tmpeggs)
