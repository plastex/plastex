from pathlib import Path

import subprocess

config_path = str((Path(__file__).parent/'sample_config').absolute())
src_path = str((Path(__file__).parent/'empty_article.tex').absolute())

def test_config_file_reading():
    """
    Check that config file provided on command line are read.
    This is a cli only test, hence difficult to test directly.
    Here we use a config file asking for a non-existant theme, then
    check a warning appears on stderr.
    """
    out = subprocess.run(['plastex', '-c', config_path, src_path], check=True,
                         stderr=subprocess.PIPE).stderr.decode()
    assert 'WARNING: Using default renderer for document-layout' in out


