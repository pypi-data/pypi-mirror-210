import functools
import importlib
import inspect
import pathlib
import sys
import typing

from .__type import FileProvider, Namespace, Provider

StrFactory = typing.Union[str, typing.Callable[[], str]]
DEFAULT_PATHS = ['config', lambda: pathlib.Path(sys.executable).parent.joinpath('config')]
DEFAULT_PROVIDERS = ['json']


class ProviderNotFoundError(Exception):
    def __init__(self, provider: str, error: Exception):
        self.provider = provider
        self.error = error

    def __str__(self):
        return f"Provider not found '{self.provider}'"


@functools.lru_cache()
def get_provider(tag: str) -> typing.Type[FileProvider]:
    try:
        module = importlib.import_module(f'configloaders.providers.{tag}_provider')
        return inspect.getmembers(module, lambda x: inspect.isclass(x) and issubclass(x, FileProvider) and x is not FileProvider)[0][1]
    except ModuleNotFoundError as e: error = e
    except IndexError as e: error = e
    raise ProviderNotFoundError(tag, error)


class DefaultProvider(Provider):
    def __init__(self, provider: str, load_paths: typing.List[StrFactory] = DEFAULT_PATHS, dump_paths: typing.List[StrFactory] = DEFAULT_PATHS[:1]):
        if ':' in provider:
            provider, path = provider.split(':')
            load_paths = path.split(',')
            dump_paths = path.split(',')
        self.provider_name = provider
        self.provider = get_provider(provider)
        self.load_paths = load_paths
        self.dump_paths = dump_paths

    def each(self, paths) -> typing.Generator[typing.Tuple[str, str], typing.Any, None]:
        for path in paths:
            suffix = '.' + self.provider_name
            if not isinstance(path, str): path = path()
            if isinstance(path, str):
                path = path.strip()
                if path[-1:] == '!': path, suffix = path[:-1], ''
            yield path, suffix

    def load(self) -> dict:
        data = {}
        for path, suffix in self.each(self.load_paths):
            try:
                data.update(self.provider(pathlib.Path(path), suffix).load())
            except FileNotFoundError: pass
        return data

    def dump(self, data: dict) -> None:
        for path, suffix in self.each(self.dump_paths):
            try:
                self.provider(pathlib.Path(path), suffix).dump(data)
            except FileNotFoundError: pass


class NamespaceProvider(Provider):
    def __init__(self, target):
        self.ns = Namespace(target)

    def load(self) -> dict:
        return self.ns.__dict__


def load(target, *providers: typing.Union[str, Provider, object], prefix: str = '') -> typing.Any:
    ns = Namespace(target)
    for provider in (providers or DEFAULT_PROVIDERS)[::-1]:
        if isinstance(provider, str): provider = DefaultProvider(provider)
        elif not isinstance(provider, Provider): provider = NamespaceProvider(provider)
        data = provider.load()
        for key in prefix.split('.'):
            if key and data: data = data.get(key)
        for key in data or []:
            ns.update(key, data[key])
    return ns.target


def dump(data, *providers: typing.Union[str, Provider, object], prefix: str = '') -> dict:
    data = Namespace(data).__dict__
    for key in prefix.split('.'):
        if key and data: data = data.get(key)
    for provider in (providers or DEFAULT_PROVIDERS)[::-1]:
        if isinstance(provider, str): provider = DefaultProvider(provider)
        provider.dump(data)
    return data


def update(data, *providers: typing.Union[str, Provider, object], prefix: str = '') -> dict:
    part = full = load({}, *providers)
    for key in prefix.split('.')[-1:]:
        if key: part = part.setdefault(key, {} if key not in part else part[key])
    load(part, data)
    for provider in (providers or DEFAULT_PROVIDERS)[::-1]:
        if isinstance(provider, str): provider = DefaultProvider(provider)
        provider.dump(full)
    return full


def config(target=None, *providers: typing.Union[str, Provider, object], prefix: str = '') -> typing.Any:
    if target is not None: return load(target, *providers, prefix=prefix)

    def decorator(target):
        return load(target, *providers, prefix=prefix)

    return decorator
