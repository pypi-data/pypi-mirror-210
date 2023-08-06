# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bovine_pubsub']

package_data = \
{'': ['*']}

install_requires = \
['quart-redis>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'bovine-pubsub',
    'version': '0.2.1',
    'description': 'A Quart Redis thing to handle pubsub tasks in particular the event source',
    'long_description': '# bovine_pubsub\n\nRequires redis. Usage see `examples/basic_app.py`.\n',
    'author': 'Helge',
    'author_email': 'helge.krueger@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://codeberg.org/bovine/bovine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
