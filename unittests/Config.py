from plasTeX.Config import defaultConfig
from plasTeX.ConfigManager import *
from argparse import ArgumentParser
from pathlib import Path
import pytest

def test_interpolate():
    config = defaultConfig()
    config["general"]["renderer"] = "HTML5"
    config["files"]["split-level"] = 5
    config["general"]["theme"] = "%(renderer)s-%%-theme-%(split-level)d"
    assert config["general"]["theme"] == "HTML5-%-theme-5"

    config["document"]["disable-charsub"] = ["%(renderer)s-foo", "%(theme)s-bar"]
    assert config["document"]["disable-charsub"] == ["HTML5-foo", "HTML5-%-theme-5-bar"]

def test_interpolate_recursion():
    config = defaultConfig()
    config["general"]["theme"] = "%(renderer)s"
    config["general"]["renderer"] = "%(theme)s"
    with pytest.raises(RecursionError):
        x = config["general"]["theme"]

def test_interpolate_fail():
    config = defaultConfig()
    config["general"]["theme"] = "%(nonexistent)s"
    with pytest.raises(KeyError):
        x = config["general"]["theme"]

def test_multistringoption():
    option = MultiStringOption("Test", "--test", ["a"])

    parser = ArgumentParser()
    group = parser.add_argument_group("test")
    option.registerArgparse(group)

    data = vars(parser.parse_args(["--test", "c", "d", "--test", "a", "c"]))
    option.updateFromDict(data)

    assert option.value == ["a", "c", "d", "a", "c"]

def test_dict_option(tmpdir):
    with tmpdir.as_cwd():
        Path("test.ini").write_text('''
[test]
foo=3
bar=5
''')
        config = ConfigManager()
        sect = config.addSection("test")

        class TestOption(DictOption[str]):
            @classmethod
            def entryFromString(cls, entry: str) -> str:
                return entry

        sect["data"] = TestOption("", "", {"baz": "6"})
        config.read("test.ini")

        assert config["test"]["data"] == {"baz": "6", "foo": "3", "bar": "5"}
