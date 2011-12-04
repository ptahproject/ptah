""" commands tests """
import sys, os
import unittest
import tempfile, shutil
from ptah import config, view
from ptah.scripts import pstatic
from pyramid.compat import NativeIO, bytes_


class TestStaticCommand(unittest.TestCase):

    def setUp(self):
        self.out = NativeIO()
        self._stdout = sys.stdout
        sys.stdout = self.out
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)

        sys.stdout = self._stdout
        shutil.rmtree(self.dir)

    def test_commands_static_list(self):
        view.static('tests', 'ptah.view.tests:static')

        sys.argv[1:] = ['-l']

        pstatic.main()

        val = self.out.getvalue()
        self.assertTrue('* tests' in val)
        self.assertTrue('by: ptah.view.tests' in val)

    def test_commands_static_dump_errors(self):
        pstatic.StaticCommand._include = ('ptah', self.__class__.__module__)

        view.static('tests', 'ptah.view.tests:static/dir2')

        _out = sys.stdout

        file = os.path.join(self.dir, 'file')
        f = open(file, 'w')
        f.write(' ')
        f.close()

        sys.argv[1:] = ['-d %s'%file]
        out = NativeIO()

        sys.stdout = out
        pstatic.main()
        sys.stdout = _out

        val = out.getvalue()
        self.assertTrue('Output path is not directory.' in val)

    def test_commands_static_dump(self):
        view.static('tests', 'ptah.view.tests:static/dir2')

        pstatic.StaticCommand._include = ('ptah', self.__class__.__module__)

        dir = os.path.join(self.dir, 'subdir')

        sys.argv[1:] = ['-d %s'%dir]

        pstatic.main()

        val = self.out.getvalue()
        self.assertTrue("* Coping from 'ptah.view.tests'" in val)

        files = sorted(os.listdir(os.path.join(dir, 'tests')))
        self.assertTrue(files == ['style.css', 'text.txt'])

    def test_commands_static_dump_skipping_existing(self):
        pstatic.StaticCommand._include = ('ptah', self.__class__.__module__)

        view.static('tests', 'ptah.view.tests:static/dir2')

        os.makedirs(os.path.join(self.dir, 'tests'))
        file = os.path.join(self.dir, 'tests', 'text.txt')
        f = open(file, 'wb')
        f.write(bytes_('test existing file','utf-8'))
        f.close()

        sys.argv[1:] = ['-d %s'%self.dir]

        pstatic.main()

        val = self.out.getvalue()
        self.assertTrue("skipping ../ptah.view.tests/text.txt" in val)
        self.assertTrue('test existing file' == open(file, 'r').read())
