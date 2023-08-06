import importlib.util
import pathlib

from ..__type import FileProvider


class PyProvider(FileProvider):
    def __init__(self, path: pathlib.Path, suffix: str, ignore_private: bool = True):
        super().__init__(path, suffix)
        self.ignore_private = ignore_private

    def read(self, path: pathlib.Path) -> dict:
        spec = importlib.util.spec_from_file_location(path.as_posix(), path)

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = vars(module)
        if self.ignore_private: data = {k: data[k] for k in data if not k.startswith('__')}
        return data
