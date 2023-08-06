import pathlib
import pickle

from ..__type import FileProvider


class PickleProvider(FileProvider):
    def read(self, path: pathlib.Path) -> dict:
        with open(path, 'rb') as file: return pickle.load(file)

    def write(self, path: pathlib.Path, data: dict) -> None:
        with open(path, 'wb') as file: pickle.dump(data, file)
