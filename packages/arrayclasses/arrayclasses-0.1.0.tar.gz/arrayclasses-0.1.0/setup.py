# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['arrayclasses']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.3,<2.0.0']

setup_kwargs = {
    'name': 'arrayclasses',
    'version': '0.1.0',
    'description': 'Analogue to dataclass that uses a numpy-backed array to store values.',
    'long_description': None,
    'author': 'Lukas Tenbrink',
    'author_email': 'lukas.tenbrink@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
