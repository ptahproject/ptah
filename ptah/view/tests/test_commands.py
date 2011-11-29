""" commands tests """
import sys, os
import unittest
import tempfile, shutil
from io import BytesIO
from ptah import config, view
from ptah.scripts import pstatic


class TestStaticCommand(unittest.TestCase):

    def setUp(self):
        self.out = BytesIO()
        self._stdout = sys.stdout
        sys.stdout = self.out
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)

        self.stdout = self._stdout
        shutil.rmtree(self.dir)

    def test_commands_static_list(self):
        view.static('tests', 'ptah.view.tests:static')

        _out = sys.stdout

        sys.argv[1:] = ['-l']

        out = BytesIO()
        sys.stdout = out
        pstatic.main()
        sys.stdout = _out

        val = out.getvalue()
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
        out = BytesIO()

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
        files = os.listdir(os.path.join(dir, 'tests'))
        files.sort()
        self.assertTrue(files == ['style.css', 'text.txt'])

    def test_commands_static_dump_skipping_existing(self):
        pstatic.StaticCommand._include = ('ptah', self.__class__.__module__)

        view.static('tests', 'ptah.view.tests:static/dir2')

        os.makedirs(os.path.join(self.dir, 'tests'))
        file = os.path.join(self.dir, 'tests', 'text.txt')
        f = open(file, 'wb')
        f.write('test existing file')
        f.close()

        sys.argv[1:] = ['-d %s'%self.dir]

        pstatic.main()

        val = self.out.getvalue()
        self.assertTrue("skipping ../ptah.view.tests/text.txt" in val)
        self.assertTrue('test existing file' == open(file, 'r').read())
