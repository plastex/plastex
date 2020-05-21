from pathlib import Path
from unittest.mock import Mock
from pytest import mark, fixture


from plasTeX.TeX import TeXDocument
from plasTeX.PackageResource import PackageResource, PackageCss, PackageTemplateDir

@fixture
def doc():
    doc = TeXDocument()
    doc.rendererdata['html'] = {}
    return doc

class PackageMyStuff(PackageResource):
    key = 'mykey'

@mark.parametrize("data, list_", [
    ('test', ['test']),
    (['test1', 'test2'], ['test1', 'test2'])])
def test_set_rendererdata(doc, data, list_):
    """Test setting rendererdata"""
    resource = PackageMyStuff(data=data, renderers='html')
    resource.alter(Mock(), rendererName='html', document=doc, target=Path())

    assert doc.rendererdata['html']['mykey'] == list_


@mark.parametrize("renderers, result", [
    ('html', True),
    ('htm.*', True),
    (['html', 'xml'], True),
    (['htm$', 'xml'], False),
    ('epub', False),
    (['epub', 'xml'], False),
    ])
def test_renderer_pattern(doc, renderers, result):
    """Test action only if renderer is targeted"""
    resource = PackageMyStuff(data='test', renderers=renderers)
    resource.alter(Mock(), rendererName='html', document=doc, target=Path())

    assert ('mykey' in doc.rendererdata['html']) == result

def test_copy_file(monkeypatch, doc):
    copy_calls = []
    def mock_copy(source, dest):
        copy_calls.append((source, dest))

    monkeypatch.setattr('plasTeX.PackageResource.shutil.copy', mock_copy)

    resource = PackageCss(path=Path('mypkg')/'mystyle.css', renderers='html')
    resource.alter(
        document=doc,
        rendererName='html',
        renderer=Mock(),
        target=Path('buildir'))

    assert copy_calls == [(str(Path('mypkg')/'mystyle.css'),
                           str(Path('buildir')/'styles'))]

def test_copy_missing_file(monkeypatch, doc):
    def mock_copy(source, dest):
        raise IOError

    monkeypatch.setattr('plasTeX.PackageResource.shutil.copy', mock_copy)
    mock_logger = Mock()
    monkeypatch.setattr('plasTeX.PackageResource.log.error', mock_logger)

    resource = PackageCss(path=Path('mypkg')/'mystyle.css', renderers='html')
    resource.alter(
        document=doc,
        rendererName='html',
        renderer=Mock(),
        target=Path('buildir'))

    assert mock_logger.call_count == 1

def test_package_template_dir(monkeypatch, doc):
    renderer = Mock()
    resource = PackageTemplateDir(renderers='html',
                                  path=Path('mypkg')/'templates')
    resource.alter(
        document=doc,
        rendererName='html',
        renderer=renderer,
        target=Path('buildir'))
    renderer.importDirectory.assert_called_with(str(Path('mypkg')/'templates'))
