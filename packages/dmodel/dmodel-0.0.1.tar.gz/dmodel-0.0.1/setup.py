# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dmodel']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dmodel',
    'version': '0.0.1',
    'description': 'models for deta space',
    'long_description': None,
    'author': 'Daniel Arantes',
    'author_email': 'arantesdv@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
