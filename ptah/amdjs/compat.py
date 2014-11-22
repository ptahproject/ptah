import os
import subprocess


def check_output(*popenargs, **kwargs):
    """python2.7 subprocess.checkoutput copy."""
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:  # pragma: nocover
        return None
    return output

try:
    import simplejson as json  # faster
except ImportError:  # pragma: no cover
    import json  # slowest

try:
    if os.sys.platform == 'win32':  # pragma: no cover
        NODE_PATH = r'C:\Program Files (x86)\nodejs\node.exe'
        os.stat(NODE_PATH)
    else:
        NODE_PATH = check_output(('which', 'nodejs')).strip()
except:  # pragma: no cover
    NODE_PATH = None

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict
