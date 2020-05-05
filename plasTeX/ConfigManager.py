from argparse import _ArgumentGroup as ArgumentGroup, ArgumentParser
from abc import ABC, abstractmethod
from typing import Dict, List, Generic, TypeVar, Any, Optional, Type, KeysView, Union
from configparser import ConfigParser
import shlex
from collections.abc import Sequence

T = TypeVar('T')

def formatDefault(s: Any):
    return " [" + str(s).replace("%", "%%") + "]"

class Option(Generic[T]):
    def __init__(self, description: str, options: str, default: T):
        self.description = description
        self.options = options.split(" ")
        self.name = self.options[0].lstrip("-")
        self.value = default

    def registerArgparse(self, group: ArgumentGroup):
        group.add_argument(*self.options, dest=self.name, type=self.valueType(), help=self.description + formatDefault(self.value))

    def valueType(self) -> Type:
        return type(self.value)

    def updateFromDict(self, data: Dict["str", Any]):
        value = data.get(self.name)
        if value is not None:
            self.value = value

    def setFromString(self, string: str):
        self.value = self.valueType()(string)

class BooleanOption(Option[bool]):
    def registerArgparse(self, group: ArgumentGroup):
        enables = [x for x in self.options if x[0] != "!"]
        disables = [x[1:] for x in self.options if x[0] == "!"]

        group.add_argument(*enables, dest=self.name, help=self.description + formatDefault(self.value), action='store_true', default=None)
        if disables:
            group.add_argument(*disables, dest=self.name, help=self.description + formatDefault(self.value), action='store_false', default=None)

class MultiStringOption(Option[List[str]]):
    def registerArgparse(self, group: ArgumentGroup):
        group.add_argument(*self.options, dest=self.name, type=str, nargs="*", help=self.description, action="append")

    def setFromString(self, string: str):
        self.value.extend(shlex.split(string))

    def updateFromDict(self, data: Dict["str", Any]):
        value = data.get(self.name)
        if value is not None:
            for entry in value:
                self.value.extend(entry)

class StringOption(Option[str]):
    pass

class FloatOption(Option[float]):
    pass

class IntegerOption(Option[int]):
    pass

class DictOption(ABC, Option[Dict[str, T]]):
    @classmethod
    @abstractmethod
    def entryFromString(cls, entry: str) -> T:
        """Converts a string into T"""

    def set(self, key: str, value: str):
        self.value[key] = self.entryFromString(value)

    def setFromString(self, string: str):
        raise ValueError("Calling setFromString on a DictOption. The individual items should be inserted with set.")

    def updateFromDict(self, data: Dict["str", Any]):
        entries = data.get(self.name) # type: Optional[Dict["str", Any]]
        if entries is not None:
            for key, val in entries.items():
                self.set(key, val)

class ConfigSection():
    def __init__(self, name: str, parent: 'ConfigManager'):
        self.name = name
        self.parent = parent
        self.data = {} # type: Dict[str, Option]

    def __getitem__(self, key: str) -> Any:
        value = self.data[key].value
        wrapper = InterpolationWrapper(self.parent)
        if isinstance(value, str):
            return value % wrapper
        elif isinstance(value, Sequence) and value and isinstance(value[0], str):
            return [x % wrapper for x in value]
        else:
            return value

    def __setitem__(self, key: str, value: Any):
        if isinstance(value, Option):
            if key in self.data:
                raise ValueError
            self.data[key] = value
        else:
            self.data[key].value = value

    def get(self, key: str, default: Optional[Any]=None) -> Optional[Any]:
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> KeysView[str]:
        return self.data.keys()

    def registerArgparse(self, parser: ArgumentParser):
        group = parser.add_argument_group(self.name)

        for option in self.data.values():
            option.registerArgparse(group)

    def updateFromDict(self, data: Dict[str, Any]):
        for option in self.data.values():
            option.updateFromDict(data)

class ConfigManager(Dict[str, ConfigSection]):
    def registerArgparse(self, parser: ArgumentParser):
        for item in self.values():
            item.registerArgparse(parser)

    def updateFromDict(self, data: Dict[str, Any]):
        for section in self.values():
            section.updateFromDict(data)

    def addSection(self, name: str, description: Optional[str]=None) -> ConfigSection:
        if name in self:
            raise ValueError("Section {} already exists".format(name))

        if description is None:
            description = name.capitalize() + " Options"

        self[name] = ConfigSection(description, self)
        return self[name]

    def read(self, filenames: Union[List[str], str]):
        """
        Loads config from an INI files in `filenames`. The function ignores
        files that do not exist.
        """

        data = ConfigParser(interpolation=None)
        data.read(filenames)

        for section in data.sections():
            if section not in self:
                print("Unrecognized section: {}".format(section))
                continue

            dictObject = next((x for x in self[section].data.values() if isinstance(x, DictOption)), None)

            for key, val in data.items(section):
                try:
                    self[section].data[key].setFromString(val)
                except KeyError:
                    if dictObject is not None:
                        dictObject.set(key, val)
                    else:
                        print("Unrecognized config: {}.{}".format(section, key))

class InterpolationWrapper(Dict[str, Any]):
    def __init__(self, config: ConfigManager):
        self.inner = config

    def __getitem__(self, key) -> Any:
        for section in self.inner.values():
            try:
                return section[key]
            except KeyError:
                continue
        raise KeyError(key)
