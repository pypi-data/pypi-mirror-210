import argparse
import functools
import inspect
import pathlib


class Namespace:
    def __init__(self, target):
        self.__target = target
        if inspect.isfunction(self.__target) or isinstance(self.__target, functools.partial):
            self.__target = functools.partial(self.__target)
            self.__signature = inspect.signature(self.__target.func).parameters
            self.__setitem_impl = self.__setitem_func
            self.__getitem_impl = self.__getitem_func
            self.__iter_impl = self.__iter_func
        elif isinstance(self.__target, dict):
            self.__setitem_impl = self.__setitem_dict
            self.__getitem_impl = self.__getitem_dict
            self.__iter_impl = self.__iter_dict
        elif isinstance(self.__target, argparse.ArgumentParser):
            self.__setitem_impl = self.__setitem_arg
            self.__getitem_impl = self.__getitem_arg
            self.__iter_impl = self.__iter_arg
        else:
            self.__setitem_impl = self.__setitem_obj
            self.__getitem_impl = self.__getitem_obj
            self.__iter_impl = self.__iter_obj

    @property
    def target(self):
        if inspect.isfunction(self.__target) or isinstance(self.__target, functools.partial):
            return lambda *args, **kwargs: self.__target(*args, **kwargs)
        return self.__target

    def update(self, key, data):
        items = [(self, key, data)]
        while len(items) > 0:
            ns, key, dat = items.pop(0)
            if key in ns and isinstance(dat, dict):
                for k in dat: items.append((Namespace(ns[key]), k, dat[k]))
            else:
                ns[key] = dat
        return self

    def __setitem__(self, key, value): return self.__setitem_impl(key, value)

    def __getitem__(self, item): return self.__getitem_impl(item)

    def __iter__(self): return self.__iter_impl()

    def __repr__(self): return '{}({})'.format(self.__class__.__name__, self.__dict__)

    def __str__(self): return '{}({})'.format(self.__class__.__name__, self.target)

    @property
    def __dict__(self):
        data = {}
        items = [(self, data)]
        while len(items) > 0:
            ns, dat = items.pop(0)
            for key in ns:
                val = ns[key]
                if isinstance(val, (int, float, str, bool, list, set, tuple, type(None))):
                    dat[key] = val
                elif not inspect.ismodule(val):
                    dat[key] = {}
                    items.append((Namespace(val), dat[key]))
        return data

    @staticmethod
    def private_key(key):
        if isinstance(key, str) and key.startswith('__'): return '__private' + key
        return key

    def __setitem_func(self, key, value):
        self.__target = functools.partial(self.__target, **dict.fromkeys([self.private_key(key)], value))

    def __getitem_func(self, item):
        item = self.private_key(item)
        if item in self.__target.keywords: return self.__target.keywords.get(item)
        else: return self.__signature[item].default

    def __iter_func(self):
        return iter(filter(lambda k: self.private_key(k) == k, self.__signature))

    def __setitem_dict(self, key, value):
        self.__target[self.private_key(key)] = value

    def __getitem_dict(self, item):
        return self.__target[self.private_key(item)]

    def __iter_dict(self):
        return iter(filter(lambda k: self.private_key(k) == k, self.__target))

    def __setitem_arg(self, key, value):
        self.__target.add_argument(f'--{self.private_key(key)}', type=type(value), default=value, metavar=str(value))

    def __getitem_arg(self, item):
        return next(filter(lambda x: x.dest == self.private_key(item), self.__target._actions)).default

    def __iter_arg(self):
        return iter(filter(lambda k: self.private_key(k) == k, map(lambda x: x.dest, self.__target._actions)))

    def __setitem_obj(self, key, value):
        setattr(self.__target, key, value)

    def __getitem_obj(self, item):
        return getattr(self.__target, item)

    def __iter_obj(self):
        return iter(filter(lambda key: not key.startswith('_'), dir(self.__target)))


class Provider:
    def load(self) -> dict: raise NotImplementedError()

    def dump(self, data: dict) -> None: raise NotImplementedError()


class FileProvider(Provider):
    def __init__(self, path: pathlib.Path, suffix: str): self.path = path.with_suffix(suffix) if suffix else path

    def load(self) -> dict: return self.read(self.path)

    def dump(self, data: dict) -> None: self.write(self.path, data)

    def read(self, path: pathlib.Path) -> dict: raise NotImplementedError()

    def write(self, path: pathlib.Path, data: dict) -> None: raise NotImplementedError()
