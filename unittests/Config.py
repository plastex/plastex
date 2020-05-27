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

def test_stringoption():
    option = StringOption("Test", "--test", "")

    parser = ArgumentParser()
    group = parser.add_argument_group("test")
    option.registerArgparse(group)

    data = vars(parser.parse_args(["--test", "foo"]))
    option.updateFromDict(data)

    assert option.value == "foo"

def test_booloption():
    option = BooleanOption("Test", "--test !--notest", False)

    parser = ArgumentParser()
    group = parser.add_argument_group("test")
    option.registerArgparse(group)

    data = vars(parser.parse_args(["--test"]))
    option.updateFromDict(data)

    assert option.value

    data = vars(parser.parse_args(["--notest"]))
    option.updateFromDict(data)

    assert not option.value

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
test=test=7,item2=8
''')
        config = ConfigManager()
        sect = config.addSection("test")

        class TestOption(DictOption[str]):
            @classmethod
            def entryFromString(cls, entry: str) -> str:
                return entry

            def registerArgparse(self, group):
                pass

        sect["test"] = TestOption("", "", {"baz": "6"})
        config.read("test.ini")

        assert config["test"]["test"] == {"baz": "6", "foo": "3", "bar": "5", "test": "7", "item2": "8"}

def test_counter(tmpdir):
    with tmpdir.as_cwd():
        Path("test.ini").write_text('''
[counters]
chapter=4
part=2
''')
        config = defaultConfig()
        config.read("test.ini")

        parser = ArgumentParser()
        config.registerArgparse(parser)
        data = vars(parser.parse_args(["--counter", "section", "4", "--counter", "subsection", "7"]))
        config.updateFromDict(data)

        assert config["counters"]["counters"] == \
                {
                    "chapter": 4,
                    "part": 2,
                    "section": 4,
                    "subsection": 7
                }

def test_logging(tmpdir):
    with tmpdir.as_cwd():
        Path("test.ini").write_text('''
[logging]
parse.environments=DEBUG
''')
        config = defaultConfig()
        config.read("test.ini")

        parser = ArgumentParser()
        config.registerArgparse(parser)
        data = vars(parser.parse_args(["--logging", "test", "INFO"]))
        config.updateFromDict(data)

        assert config["logging"]["logging"] == \
                {
                    "parse.environments": "DEBUG",
                    "test": "INFO",
                }

def test_links(tmpdir):
    with tmpdir.as_cwd():
        Path("test.ini").write_text('''
[links]
next-url=https://example.com
next-title=The Next Document
mylink-title=AnotherTitle
''')
        config = defaultConfig()
        config.read("test.ini")

        parser = ArgumentParser()
        config.registerArgparse(parser)
        data = vars(parser.parse_args(["--link", "prev", "https://example.com/2", "Prev Document", "--link", "secondlink", "ATitle"]))
        config.updateFromDict(data)

        assert config["links"]["links"] == {
                "next-url": "https://example.com",
                "next-title": "The Next Document",
                "mylink-title": "AnotherTitle",
                "prev-url": "https://example.com/2",
                "prev-title": "Prev Document",
                "secondlink-title": "ATitle",
            }
