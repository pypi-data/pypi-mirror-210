# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['_version']

package_data = \
{'': ['*']}

install_requires = \
['databind.core>=4.3.0,<5.0.0', 'databind.json>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'databind',
    'version': '4.3.0',
    'description': 'Databind is a library inspired by jackson-databind to de-/serialize Python dataclasses. The `databind` package will install the full suite of databind packages. Compatible with Python 3.7 and newer.',
    'long_description': '<h1 align="center">databind</h1>\n\n<p align="center">\n  <img src="https://img.shields.io/pypi/pyversions/databind?style=for-the-badge" alt="Python versions">\n  <a href="https://pypi.org/project/databind/"><img src="https://img.shields.io/pypi/v/databind?style=for-the-badge"></a>\n</p>\n<p align="center"><i>\nDatabind is a Python serialization library on top of dataclasses, inspired by similar libraries from other languages\nlike <a href="https://github.com/FasterXML/jackson-databind">jackson-databind</a> and <a href="https://serde.rs/">serde-rs</a>.</i>\n</p>\n<p align="center">\n  <a href="https://niklasrosenstein.github.io/python-databind/core/basic-usage/">CORE Guide</a> |\n  <a href="https://niklasrosenstein.github.io/python-databind/json/examples/">JSON Examples</a>\n</p>\n\n## Overview 📖\n\nThe `databind.core` package provides the core framework for databind. It is then used by `databind.json` to provide\ncomprehensive serializatio support between Python and JSON-like data structure. The serialization can easily be\nextended to YAML or TOML by combining it with respective libraries (e.g. `pyaaml` and `tomli`).\n\n```python\n@dataclass\nclass Server:\n    host: str\n    port: int\n\n@dataclass\nclass Config:\n    server: Server\n\nfrom databind.json import dump, load\nassert load({"server": {"host": "localhost", "port": 8080}}, Config) == Config(server=Server(host=\'localhost\', port=8080))\nassert dump(Config(server=Server(host=\'localhost\', port=8080)), Config) == {"server": {"host": "localhost", "port": 8080}}\n```\n\nIf you install the `databind` proxy package, you get matching versions of `databind.core` and `databind.json`.\n\n## Features ✨\n\n  [typeapi]: https://github.com/NiklasRosenstein/python-typeapi\n\n* Support for a plethora of builtin types, including `Enum`, `Decimal`, `UUID`, `Path`, `datetime`, `date`, `time`, `timedelta`\n* Support for multiple union serialization modes (nested, flat, keyed, `typing.Literal`)\n* Support for generic types, e.g. `load([{"name": "Jane Doe"}], list[Person])`\n* Support for new-style type hints in older Python versions when using forward refererences (strings or `__future__.annotations`) thanks to [typeapi][]\n    * [PEP 604 - Allow writing union types as X | Y](https://www.python.org/dev/peps/pep-0604/)\n    * [PEP585 - Type Hinting Generics in Standard Collections](https://www.python.org/dev/peps/pep-0585/))\n* Support for customized serialization and deserialization of types\n* Support for flattening fields of a nested dataclass or collecting remaining fields in a `dict`\n* Full runtime type checking during serialization\n* Use "settings" to customize serialization behaviour\n    * As global settings per `load()`/`dump()` call: `load(..., settings=[ExtraKeys(True)])`\n    * As class-level settings using a decorator: `@Union(style=Union.FLAT)` or `@ExtraKeys(True)`\n    * As type-hint level settings using `typing.Annotated` (or `typing_extensions.Annotated`): `full_name: Annotated[str, Alias("fullName")]` or `FullNameField = Annotated[str, Alias("fullName")]`\n\n---\n\n<p align="center">Copyright &copy; 2022 &ndash; Niklas Rosenstein</p>\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.3,<4.0.0',
}


setup(**setup_kwargs)
