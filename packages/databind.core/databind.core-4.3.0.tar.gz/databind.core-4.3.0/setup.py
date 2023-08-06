# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['core', 'core.tests']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.12,<2.0.0',
 'nr-date>=2.0.0,<3.0.0',
 'nr-stream>=1.0.0,<2.0.0',
 'typeapi>=1.4.2,<2.0.0',
 'typing-extensions>=3.10.0']

setup_kwargs = {
    'name': 'databind.core',
    'version': '4.3.0',
    'description': 'Databind is a library inspired by jackson-databind to de-/serialize Python dataclasses. Compatible with Python 3.7 and newer.',
    'long_description': '# `databind.core`\n\nThis library provides the core functionality to implement serialization functions to and from Python objects, with\na great support for many features of the Python type system. A JSON implementation is provided by the `databind.json`\npackage.\n\n---\n\n<p align="center">Copyright &copy; 2020 &ndash; Niklas Rosenstein</p>\n',
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
