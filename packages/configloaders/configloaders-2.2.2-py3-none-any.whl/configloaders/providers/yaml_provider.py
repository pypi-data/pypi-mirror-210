import pathlib

import yaml

from ..__type import FileProvider


class YAMLProvider(FileProvider):
    def read(self, path: pathlib.Path) -> dict:
        with open(path, 'r', encoding='utf-8') as file: return yaml.safe_load(file)

    def write(self, path: pathlib.Path, data: dict) -> None:
        with open(path, 'w', encoding='utf-8') as file: yaml.safe_dump(data, file)
