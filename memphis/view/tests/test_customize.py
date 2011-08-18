""" tests for customize """
import unittest, signal
import os, tempfile, shutil, time
from memphis import config, view
from memphis.view import customize
from memphis.config import shutdown

from base import Base


class BaseLayerTest(Base):

    file1 = "<div>Test template 1</div>"
    file2 = "<div>Test template 2</div>"

    def _setup_memphis(self):
        pass

    def _mkfile1(self, content):
        f = open(os.path.join(self.dir1, 'file.pt'), 'wb')
        f.write(content)
        f.close()

    def _mkfile2(self, content, name='file.pt'):
        f = open(os.path.join(self.dir2, 'memphis.view.tests', name), 'wb')
        f.write(content)
        f.close()

    def setUp(self):
        Base.setUp(self)
        
        self.dir1 = tempfile.mkdtemp()
        self.dir2 = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.dir2, 'memphis.view.tests'))
        
    def tearDown(self):
        Base.tearDown(self)

        shutil.rmtree(self.dir1)
        shutil.rmtree(self.dir2)

        for handler in shutdown.handlers:
            handler()

      
class TestGlobalCustomizeManagement(BaseLayerTest):

    def test_customize_global_disabled(self):
        self._init_memphis()

        self.assertEqual('', customize.TEMPLATE.custom)

    def test_customize_global_enabled(self):
        self._mkfile1(self.file1)
        self._mkfile2(self.file2)

        tmpl = view.template(os.path.join(self.dir1, 'file.pt'))
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

        # enable custom folder
        self._init_memphis({'template.custom': self.dir2})

        self.assertEqual(tmpl(), '<div>Test template 2</div>')

    def test_customize_global_custom_layer_name(self):
        self._mkfile1(self.file1)

        tmpl = view.template(os.path.join(self.dir1, 'file.pt'),
                             layer='layer')
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

        os.makedirs(os.path.join(self.dir2, 'layer'))
        f = open(os.path.join(self.dir2, 'layer', 'file.pt'), 'wb')
        f.write(self.file2)
        f.close()

        # enable custom folder
        self._init_memphis({'template.custom': self.dir2})

        self.assertEqual(tmpl(), '<div>Test template 2</div>')

    def test_customize_global_reenable(self):
        self._mkfile1(self.file1)
        self._mkfile2(self.file2)

        f = open(os.path.join(self.dir2, 'test'), 'wb')
        f.write(' ')
        f.close()

        tmpl = view.template(os.path.join(self.dir1, 'file.pt'))
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

        # load without watcher
        self._init_memphis({'template.custom': os.path.join(self.dir2, 'test')})

        self.assertTrue(customize.TEMPLATE._manager is None)
        self.assertTrue(customize.TEMPLATE._watcher is None)
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

        # reinitialize
        customize.TEMPLATE['custom'] = self.dir2
        customize.TEMPLATE['watcher'] = ''
        customize.initialize(None)

        self.assertTrue(customize.TEMPLATE._manager is not None)
        self.assertTrue(customize.TEMPLATE._watcher is None)

        self.assertEqual(tmpl(), '<div>Test template 2</div>')

    def test_customize_global_disable(self):
        self._mkfile1(self.file1)
        self._mkfile2(self.file2)

        tmpl = view.template(os.path.join(self.dir1, 'file.pt'))
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

        # enable custom folder
        self._init_memphis({'template.custom': self.dir2})
        self.assertEqual(tmpl(), '<div>Test template 2</div>')

        customize.TEMPLATE['custom'] = ''
        customize.initialize(None)

        self.assertTrue(customize.TEMPLATE._manager is None)
        self.assertTrue(customize.TEMPLATE._watcher is None)
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

    def test_customize_global_createfolder_and_reloadpackage(self):
        self._mkfile1(self.file1)

        tmpl = view.template(os.path.join(self.dir1, 'file.pt'))
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

        self.dir2 = os.path.join(self.dir2, 'test')

        # enable custom folder
        self._init_memphis({'template.custom': self.dir2})

        self.assertTrue(os.path.isdir(self.dir2))
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

        # create new custom resource
        os.mkdir(os.path.join(self.dir2, 'memphis.view.tests'))
        self._mkfile2(self.file2)
        time.sleep(0.1)

        # template reloaded
        self.assertEqual(tmpl(), '<div>Test template 2</div>')

        # remove template
        shutil.rmtree(os.path.join(self.dir2, 'memphis.view.tests'))

        time.sleep(0.1)
        self.assertEqual(tmpl(), '<div>Test template 1</div>')

    def test_customize_global_initialization_exc(self):
        orig = customize.iNotifyWatcher.start
        def start(self):
            raise 'Error'

        customize.iNotifyWatcher.start = start

        # enable custom folder
        self._init_memphis({'template.custom': self.dir2})
        self.assertTrue(not customize.TEMPLATE._watcher._started)

        customize.iNotifyWatcher.start = orig

    # fixme: implement
    def test_customize_global_and_layers(self):
        pass


class TestTemplateLayer(BaseLayerTest):

    def test_customize_layers(self):
        self.dir3 = tempfile.mkdtemp()

        self._mkfile1(self.file1)
        f = open(os.path.join(self.dir1, 'file2.pt'), 'wb')
        f.write(self.file2)
        f.close()

        tmpl1 = view.template(os.path.join(self.dir1, 'file.pt'))
        tmpl2 = view.template(os.path.join(self.dir1, 'file2.pt'))
        self.assertEqual(tmpl1(), '<div>Test template 1</div>')
        self.assertEqual(tmpl2(), '<div>Test template 2</div>')

        # layers
        view.layer('memphis.view.tests', self.dir2)
        view.layer('memphis.view.tests', self.dir3)

        # override file.pt
        f = open(os.path.join(self.dir2, 'file.pt'), 'wb')
        f.write(self.file2)
        f.close()
               
        # override file2.pt
        f = open(os.path.join(self.dir3, 'file2.pt'), 'wb')
        f.write(self.file1)
        f.close()

        # initialize layers
        customize._Manager.initialize()

        self.assertEqual(tmpl1(), '<div>Test template 2</div>')
        self.assertEqual(tmpl2(), '<div>Test template 1</div>')

    def test_customize_layers_with_custom_name(self):
        self.dir3 = tempfile.mkdtemp()

        self._mkfile1(self.file1)
        f = open(os.path.join(self.dir1, 'file2.pt'), 'wb')
        f.write(self.file2)
        f.close()

        tmpl1 = view.template(os.path.join(self.dir1, 'file.pt'),
                              layer = 'layer')
        tmpl2 = view.template(os.path.join(self.dir1, 'file2.pt'),
                              layer = 'layer')
        self.assertEqual(tmpl1(), '<div>Test template 1</div>')
        self.assertEqual(tmpl2(), '<div>Test template 2</div>')

        # layers
        view.layer('layer', self.dir2)
        view.layer('layer', self.dir3)

        # override file.pt
        f = open(os.path.join(self.dir2, 'file.pt'), 'wb')
        f.write(self.file2)
        f.close()
               
        # override file2.pt
        f = open(os.path.join(self.dir3, 'file2.pt'), 'wb')
        f.write(self.file1)
        f.close()

        # initialize layers
        customize._Manager.initialize()

        self.assertEqual(tmpl1(), '<div>Test template 2</div>')
        self.assertEqual(tmpl2(), '<div>Test template 1</div>')
