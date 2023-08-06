import pathlib

import toml

from ..__type import FileProvider


class TOMLProvider(FileProvider):
    def read(self, path: pathlib.Path) -> dict:
        with open(path, 'r', encoding='utf-8') as file: return toml.load(file)

    def write(self, path: pathlib.Path, data: dict) -> None:
        with open(path, 'w', encoding='utf-8') as file: toml.dump(data, file)
