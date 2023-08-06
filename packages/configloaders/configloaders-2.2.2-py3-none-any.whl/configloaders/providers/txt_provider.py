import pathlib
import typing

from ..__type import FileProvider


class TXTProvider(FileProvider):
    def __init__(self, path: pathlib.Path, suffix: str, key: typing.Callable[[int], typing.Any] = lambda i: i):
        super().__init__(path, suffix)
        self.key = key

    def read(self, path: pathlib.Path) -> dict:
        with open(path, 'r', encoding='utf-8') as file: return {self.key(i): line for i, line in enumerate(file.readlines())}

    def write(self, path: pathlib.Path, data: dict) -> None:
        with open(path, 'w', encoding='utf-8') as file: file.writelines([str(line) for i, line in data.items() if isinstance(i, int)])
