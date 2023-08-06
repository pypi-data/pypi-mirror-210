# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dtbase']

package_data = \
{'': ['*']}

install_requires = \
['deta[async]==1.1.0a2', 'dhint>=0.0.5,<0.0.6', 'starlette>=0.27.0,<0.28.0']

setup_kwargs = {
    'name': 'dtbase',
    'version': '0.0.2',
    'description': '',
    'long_description': None,
    'author': 'Daniel Arantes',
    'author_email': 'arantesdv@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
