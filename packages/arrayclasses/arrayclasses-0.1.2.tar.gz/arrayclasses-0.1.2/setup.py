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
    'version': '0.1.2',
    'description': 'Analogue to dataclass that uses a numpy-backed array to store values.',
    'long_description': '# arrayclass\n\nA small `@dataclass`-like decorator for python classes. The class will store its values in a single contiguous [numpy](https://numpy.org) array. It can also be converted to and from plain numpy arrays.\n\n## Installation\n\n`poetry add dataclasses` or `pip install dataclasses`\n\n## Usage\n\n```py\nimport arrayclasses\n\n@arrayclasses.arrayclass\nclass State:\n    x: float\n    y: tuple[float, float]\n    z: float\n\n# Object creation\nstate = State(x=5, y=(0, 1), z=0)\nprint(np.x)  # Prints 5.0\nprint(np.y)  # Prints np.array([0.0, 1.0])\nstate.y = 2.0\nprint(np.y)  # Prints np.array([2.0, 2.0])\n\n# Array conversion.\nstate = arrayclasses.from_array((5, 0, 1, 0))\nprint(np.array(state))  # prints np.array([5.0, 0.0, 1.0, 0.0])\n```\n',
    'author': 'Lukas Tenbrink',
    'author_email': 'lukas.tenbrink@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ivorforce/python-arrayclass',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
