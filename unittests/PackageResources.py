import os
from pytest import mark, fixture

try:
    from unittest.mock import Mock 
except ImportError:
    from mock import Mock

from plasTeX.TeX import TeXDocument
from plasTeX.PackageResource import PackageResource, PackageCss, rendererDir, PackageTemplateDir
from plasTeX.Renderers.PageTemplate import Renderer

@fixture
def doc():
    doc = TeXDocument()
    doc.rendererdata['html'] = {}
    return doc
 
@mark.parametrize("data, list_", [
    ('test', ['test']),
    (['test1', 'test2'], ['test1', 'test2'])])
def test_set_rendererdata(doc, data, list_):
    """Test setting rendererdata"""
    resource = PackageResource(key='mykey', data=data, renderers='html')
    resource.alter(document=doc, rendererName='html')

    assert doc.rendererdata['html']['mykey'] == list_


@mark.parametrize("renderers, result", [
    ('html', True),
    ('htm.*', True),
    (['html', 'xml'], True),
    (['htm$', 'xml'], False),
    ('epub', False),
    (['epub', 'xml'], False),
    ])
def test_doIt(doc, renderers, result):
    """Test action only if renderer is targeted"""
    resource = PackageResource(key='mykey', data='test', renderers=renderers)
    resource.alter(document=doc, rendererName='html')

    assert ('mykey' in doc.rendererdata['html']) == result

def test_copy_from_renderer_dir(monkeypatch, doc):
    copy_calls = []
    def mock_copy(source, dest):
        if not source.startswith('html'):
            raise IOError
        copy_calls.append((source, dest))

    monkeypatch.setattr('plasTeX.PackageResource.shutil.copy', mock_copy)
    monkeypatch.setattr(
        'plasTeX.PackageResource.rendererDir', 
        lambda x: 'html')

    resource = PackageCss(data='mystyle.css', package='mypkg', renderers='html')
    resource.alter(
        document=doc, 
        rendererName='html',
        renderer=object(),
        target='buildir')

    assert copy_calls == [(
        os.path.join('html', 'mypkg', 'mystyle.css'), 
        os.path.join('buildir', 'styles'))]

def test_copy_from_working_dir(monkeypatch, doc):
    copy_calls = []
    def mock_copy(source, dest):
        copy_calls.append((source, dest))

    monkeypatch.setattr('plasTeX.PackageResource.shutil.copy', mock_copy)
    monkeypatch.setattr(
        'plasTeX.PackageResource.rendererDir', 
        lambda x: 'html')

    doc.userdata['working-dir'] = 'mydir'
    resource = PackageCss(data='mystyle.css', package='mypkg', renderers='html')
    resource.alter(
        document=doc, 
        rendererName='html',
        renderer=object(),
        target='buildir')


    assert copy_calls == [(
        os.path.join('mydir', 'mypkg', 'mystyle.css'), 
        os.path.join('buildir', 'styles'))]

def test_copy_missing_file(monkeypatch, doc):
    def mock_copy(source, dest):
        raise IOError

    monkeypatch.setattr('plasTeX.PackageResource.shutil.copy', mock_copy)
    monkeypatch.setattr(
        'plasTeX.PackageResource.rendererDir', 
        lambda x: 'html')

    mock_logger = Mock()
    monkeypatch.setattr('plasTeX.PackageResource.log.error', mock_logger)

    resource = PackageCss(data='mystyle.css', package='mypkg', renderers='html')
    resource.alter(
        document=doc, 
        rendererName='html',
        renderer=object(),
        target='buildir')

    assert mock_logger.call_count == 1

def test_rendererDir():
    base = os.path.split(os.path.split(__file__)[0])[0]
    path = os.path.join(base, 'plasTeX', 'Renderers', 'PageTemplate')
    assert rendererDir(Renderer()) == path

def test_package_template_dir_user_dir(monkeypatch, doc):
    renderer = Mock()
    resource = PackageTemplateDir(renderers='html', package='mypkg')
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    monkeypatch.setattr(
        'plasTeX.PackageResource.rendererDir', 
        lambda x: 'html')


    resource.alter(
        document=doc, 
        rendererName='html',
        renderer=renderer,
        target='buildir')
    renderer.importDirectory.assert_called_with('mypkg'+os.sep)

def test_package_template_dir_renderer_dir(monkeypatch, doc):
    renderer = Mock()
    resource = PackageTemplateDir(renderers='html', package='mypkg')
    monkeypatch.setattr('os.path.isdir', lambda x: 'html' in x)
    monkeypatch.setattr(
        'plasTeX.PackageResource.rendererDir', 
        lambda x: 'html')


    resource.alter(
        document=doc, 
        rendererName='html',
        renderer=renderer,
        target='buildir')
    renderer.importDirectory.assert_called_with(os.path.join('html','mypkg', ''))

def test_package_template_dir_missing(monkeypatch, doc):
    renderer = Mock()
    resource = PackageTemplateDir(renderers='html', package='mypkg')
    monkeypatch.setattr('os.path.isdir', lambda x: False)
    monkeypatch.setattr(
        'plasTeX.PackageResource.rendererDir', 
        lambda x: 'html')
    mock_logger = Mock()
    monkeypatch.setattr('plasTeX.PackageResource.log.error', mock_logger)


    resource.alter(
        document=doc, 
        rendererName='html',
        renderer=renderer,
        target='buildir')


    assert mock_logger.call_count == 1
