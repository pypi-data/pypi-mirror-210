import configparser
import copy
import pathlib

from ..__type import FileProvider


class INIProvider(FileProvider):
    def __init__(self, path: pathlib.Path, suffix: str, default_section: str = 'DEFAULT'):
        super().__init__(path, suffix)
        self.default_section = default_section

    def read(self, path: pathlib.Path) -> dict:
        parser = configparser.ConfigParser()
        parser.read(path)
        data = {k: {kk: parser[k][kk] for kk in parser[k]} for k in dict(parser)}
        data.update(data.get(self.default_section) or {})
        return data

    def write(self, path: pathlib.Path, data: dict) -> None:
        data = copy.copy(data)
        data[self.default_section].update({k: v for k, v in data.items() if not isinstance(v, dict)})
        data = {k: v for k, v in data.items() if isinstance(v, dict)}
        parser = configparser.ConfigParser()
        parser.read_dict(data)
        with open(path, 'w', encoding='utf-8') as file:
            parser.write(file)
