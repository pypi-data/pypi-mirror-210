# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pixeldb']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pixeldb',
    'version': '1.1.3',
    'description': 'A simple database written in Python.',
    'long_description': None,
    'author': 'PxlmastrXD',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
