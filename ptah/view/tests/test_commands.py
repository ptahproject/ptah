""" commands tests """
import sys, os
import unittest
import tempfile, shutil
from cStringIO import StringIO
from paste.script.command import run
from ptah import config, view


class TestStaticCommand(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()
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

        sys.argv[:] = ['paste', 'static', '-l']

        out = StringIO()
        sys.stdout = out

        try:
            print run()
        except SystemExit:
            pass

        sys.stdout = _out

        val = out.getvalue()
        self.assertTrue('* tests' in val)
        self.assertTrue('by: ptah.view.tests' in val)

    def test_commands_static_dump_errors(self):
        from ptah.view.commands import StaticCommand
        StaticCommand._include = ('ptah', self.__class__.__module__)

        view.static('tests', 'ptah.view.tests:static/dir2')

        _out = sys.stdout

        file = os.path.join(self.dir, 'file')
        f = open(file, 'w')
        f.write(' ')
        f.close()

        sys.argv[:] = ['paste', 'static', '-d %s'%file]
        out = StringIO()
        sys.stdout = out

        try:
            run()
        except SystemExit:
            pass

        sys.stdout = _out
        val = out.getvalue()
        self.assertTrue('Output path is not directory.' in val)

    def test_commands_static_dump(self):
        view.static('tests', 'ptah.view.tests:static/dir2')

        from ptah.view.commands import StaticCommand
        StaticCommand._include = ('ptah', self.__class__.__module__)

        dir = os.path.join(self.dir, 'subdir')

        sys.argv[:] = ['paste', 'static', '-d %s'%dir]
        try:
            run()
        except SystemExit:
            pass

        val = self.out.getvalue()
        self.assertTrue("* Coping from 'ptah.view.tests'" in val)
        files = os.listdir(os.path.join(dir, 'tests'))
        files.sort()
        self.assertTrue(files == ['style.css', 'text.txt'])

    def test_commands_static_dump_skipping_existing(self):
        from ptah.view.commands import StaticCommand
        StaticCommand._include = ('ptah', self.__class__.__module__)

        view.static('tests', 'ptah.view.tests:static/dir2')

        os.makedirs(os.path.join(self.dir, 'tests'))
        file = os.path.join(self.dir, 'tests', 'text.txt')
        f = open(file, 'wb')
        f.write('test existing file')
        f.close()

        sys.argv[:] = ['paste', 'static', '-d %s'%self.dir]
        try:
            run()
        except SystemExit:
            pass

        val = self.out.getvalue()
        self.assertTrue("skipping ../ptah.view.tests/text.txt" in val)
        self.assertTrue('test existing file' == open(file, 'r').read())
