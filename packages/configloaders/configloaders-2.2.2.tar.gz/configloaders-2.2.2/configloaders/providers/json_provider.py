import json
import pathlib

from ..__type import FileProvider


class JSONProvider(FileProvider):
    def read(self, path: pathlib.Path) -> dict:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write(self, path: pathlib.Path, data: dict) -> None:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file)
