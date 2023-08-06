# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['configloaders', 'configloaders.providers']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['configloaders = configloaders.__main__:main']}

setup_kwargs = {
    'name': 'configloaders',
    'version': '2.2.2',
    'description': 'Configloaders is a Python library that allows you to easily load configuration from various types of configuration files and inject them into various types of objects, such as classes, dictionaries, functions, and methods.',
    'long_description': "# Configloaders\n\nConfigloaders is a Python library that allows you to easily load configuration from various types of configuration files and inject them into various types of objects, such as classes, dictionaries, functions, and methods.\n\n## Installation\n\nYou can install Configloaders using pip:\n\n```bash\npip install configloaders\n```\n\n## Usage\n\n### Loading configuration from a file\n\nConfigloaders supports loading configuration from various types of configuration files, including YAML, JSON, INI, and Python files.\n\n```python\nimport configloaders\n\nname = 'jack'\nage = 18\n\nconfigloaders.load(globals())\n```\n\n### Injecting configuration into an object or class\n\nConfigloaders supports injecting configuration into various types of objects, including classes, dictionaries, functions, and methods.\n\n```python\nimport configloaders\n\n@configloaders.config\nclass config:\n    name = 'jack'\n    age = 18\n```\n\n### Using configuration in a function or method\n\nConfigloaders supports using configuration in a function or method by using the `@config` decorator.\n\n```python\nimport configloaders\n\n@configloaders.config\ndef hello(name, age):\n    print(name, age)\n```\n\n### Supported file formats\n\nConfigloaders supports the following file formats:\n\n- JSON\n- INI\n- PICKLE\n- PY\n- TOML\n- TXT\n- XML\n- YAML\n\n### Supported object types\n\nConfigloaders supports the following object types:\n\n- Classes\n- Dictionaries\n- Functions\n- Methods\n- argparse.ArgumentParser\n\n## Contributing\n\nIf you would like to contribute to Configloaders, please submit a pull request or open an issue on GitHub.\n\n## License\n\nConfigloaders is licensed under the MIT License. See the LICENSE file for more information.",
    'author': 'jawide',
    'author_email': '596929059@qq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
