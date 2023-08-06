# Configloaders

Configloaders is a Python library that allows you to easily load configuration from various types of configuration files and inject them into various types of objects, such as classes, dictionaries, functions, and methods.

## Installation

You can install Configloaders using pip:

```bash
pip install configloaders
```

## Usage

### Loading configuration from a file

Configloaders supports loading configuration from various types of configuration files, including YAML, JSON, INI, and Python files.

```python
import configloaders

name = 'jack'
age = 18

configloaders.load(globals())
```

### Injecting configuration into an object or class

Configloaders supports injecting configuration into various types of objects, including classes, dictionaries, functions, and methods.

```python
import configloaders

@configloaders.config
class config:
    name = 'jack'
    age = 18
```

### Using configuration in a function or method

Configloaders supports using configuration in a function or method by using the `@config` decorator.

```python
import configloaders

@configloaders.config
def hello(name, age):
    print(name, age)
```

### Supported file formats

Configloaders supports the following file formats:

- JSON
- INI
- PICKLE
- PY
- TOML
- TXT
- XML
- YAML

### Supported object types

Configloaders supports the following object types:

- Classes
- Dictionaries
- Functions
- Methods
- argparse.ArgumentParser

## Contributing

If you would like to contribute to Configloaders, please submit a pull request or open an issue on GitHub.

## License

Configloaders is licensed under the MIT License. See the LICENSE file for more information.