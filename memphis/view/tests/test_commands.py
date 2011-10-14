""" commands tests """
import sys, os
import unittest
import tempfile, shutil
from cStringIO import StringIO
from paste.script.command import run
from memphis import config, view


class TestStaticCommand(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()
        self._stdout = sys.stdout
        sys.stdout = self.out
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        self.stdout = self._stdout
        shutil.rmtree(self.dir)

    def test_commands_static_list(self):
        view.static('tests', 'memphis.view.tests:static')

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
        self.assertTrue('by: memphis.view.tests' in val)

    def test_commands_static_dump_errors(self):
        view.static('tests', 'memphis.view.tests:static/dir2')

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
        view.static('tests', 'memphis.view.tests:static/dir2')

        dir = os.path.join(self.dir, 'subdir')

        sys.argv[:] = ['paste', 'static', '-d %s'%dir]
        try:
            run()
        except SystemExit:
            pass

        val = self.out.getvalue()
        self.assertTrue("* Coping from 'memphis.view.tests'" in val)
        self.assertTrue(os.listdir(os.path.join(dir, 'tests')) ==
                        ['text.txt', 'style.css'])

    def test_commands_static_dump_skipping_existing(self):
        view.static('tests', 'memphis.view.tests:static/dir2')

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
        self.assertTrue("skipping ../memphis.view.tests/text.txt" in val)
        self.assertTrue('test existing file' == open(file, 'r').read())


class TestTemplatesCommand(unittest.TestCase):

    def setUp(self):
        self.tmpl = view.template('memphis.view.tests:/templates/test.pt')
        self.out = StringIO()
        self._stdout = sys.stdout
        sys.stdout = self.out
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        self.stdout = self._stdout
        shutil.rmtree(self.dir)
        config.cleanUp()

    def _run(self):
        try:
            run()
        except SystemExit:
            pass
        return self.out.getvalue()

    def test_commands_template_all(self):
        sys.argv[:] = ['paste', 'templates', '-a']

        val = self._run()
        self.assertTrue('* memphis.view.tests' in val)
        self.assertTrue(
            '- test.pt: ../memphis/view/tests/templates/test.pt' in val)

    def test_commands_template_all_several_pkg(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')

        sys.argv[:] = ['paste', 'templates', '-a']

        val = self._run()

        self.assertTrue('* memphis.view' in val)
        self.assertTrue('* memphis.view.tests' in val)
        self.assertTrue(
            '- test.pt: ../memphis/view/tests/templates/test.pt' in val)

    def test_commands_template_list(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt',
                             title='Test template title',
                             description = 'Test template description')

        sys.argv[:] = ['paste', 'templates', '-l', 'memphis.view']

        val = self._run()

        self.assertTrue('* memphis.view' in val)
        self.assertTrue('* memphis.view.tests' not in val)
        self.assertTrue('Test template title' in val)
        self.assertTrue('Test template description' in val)

    # fixme: doesnt work
    def test_commands_template_custom_layer_name(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt',
                             layer = 'test-unknown')

        sys.argv[:] = ['paste', 'templates', '-l', 'test-unknown']

        val = self._run()

        #self.assertTrue('* test-unknown' in val)
        #self.assertTrue(
        #    '- test.pt: ../memphis/view/tests/templates/test.pt' in val)

    # fixme: implement
    def test_commands_template_list_with_ovveriden(self):
        pass

    def test_commands_template_print_error1(self):
        sys.argv[:] = ['paste', 'templates', '-p', 'wrongformat']

        val = self._run()

        self.assertTrue('Template path format is wrong' in val)

    def test_commands_template_print_error2(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')
        sys.argv[:] = ['paste', 'templates', '-p', 'unknownpkg:filename']

        val = self._run()

        self.assertTrue("Can't find package 'unknownpkg'" in val)

    def test_commands_template_print_error3(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')
        sys.argv[:] = ['paste', 'templates', '-p', 'memphis.view:filename']

        val = self._run()
        self.assertTrue("Can't find template 'filename'" in val)

    def test_commands_template_print(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt',
                             title='Test template title',
                             description = 'Test template description')

        sys.argv[:] = ['paste', 'templates', '-p', 'memphis.view:test.pt']

        val = self._run()
        self.assertTrue('Test template title' in val)
        self.assertTrue('Test template description' in val)
        self.assertTrue('Package:  memphis.view' in val)
        self.assertTrue('Template: test.pt' in val)
        self.assertTrue('<div>My snippet</div>' in val)

    def test_commands_template_customize_error1(self):
        sys.argv[:] = ['paste', 'templates', '-c', 'wrongformat']

        val = self._run()

        self.assertTrue('Template path format is wrong' in val)

    def test_commands_template_customize_error2(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')
        sys.argv[:] = ['paste', 'templates', '-c', 'unknownpkg:filename']

        val = self._run()

        self.assertTrue("Can't find package 'unknownpkg'" in val)

    def test_commands_template_customize_error3(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')
        sys.argv[:] = ['paste', 'templates', '-c', 'memphis.view:filename']

        val = self._run()
        self.assertTrue("Can't find template 'filename'" in val)

    def test_commands_template_customize_error4(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')
        sys.argv[:] = ['paste', 'templates', '-c', 'memphis.view:test.pt']

        val = self._run()
        self.assertTrue("Output directory is required, use -o CUSTOMDIR" in val)

    def test_commands_template_customize_error5(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')

        file = os.path.join(self.dir, 'file')
        f = open(file, 'wb')
        f.write(' ')
        f.close()

        sys.argv[:] = ['paste', 'templates', '-c', 'memphis.view:test.pt',
                       '-o', file]

        val = self._run()
        self.assertTrue("Custom path is not a directory:" in val)

    def test_commands_template_customize(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')

        sys.argv[:] = ['paste', 'templates', '-c', 'memphis.view:test.pt',
                       '-o', self.dir]

        val = self._run()

        self.assertTrue(
            "Template 'memphis.view:test.pt' has been customized" in val)
        self.assertEqual(
            open(os.path.join(self.dir, 'memphis.view', 'test.pt'),'rb').read(),
            '<div>My snippet</div>\n')

    def test_commands_template_skip_existing(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')

        os.makedirs(os.path.join(self.dir, 'memphis.view'))
        open(os.path.join(self.dir, 'memphis.view', 'test.pt'),'wb').write(
            'my customized template')

        sys.argv[:] = ['paste', 'templates', '-c', 'memphis.view:test.pt',
                       '-o', self.dir]

        val = self._run()
        self.assertTrue("Custom file 'test.pt' already exists" in val)
        self.assertEqual(
            open(os.path.join(self.dir, 'memphis.view', 'test.pt'),'rb').read(),
            'my customized template')

    def test_commands_template_force_override(self):
        tmpl = view.template('memphis.view:/tests/templates/test.pt')

        os.makedirs(os.path.join(self.dir, 'memphis.view'))
        open(os.path.join(self.dir, 'memphis.view', 'test.pt'),'w').write(
            'my customized template')

        sys.argv[:] = ['paste', 'templates', '-c', 'memphis.view:test.pt',
                       '-o', self.dir, '--force']

        val = self._run()
        self.assertTrue("Overrids: Template 'memphis.view:test.pt' has been customized." in val)
        self.assertEqual(
            open(os.path.join(self.dir, 'memphis.view', 'test.pt'),'rb').read(),
            '<div>My snippet</div>\n')
