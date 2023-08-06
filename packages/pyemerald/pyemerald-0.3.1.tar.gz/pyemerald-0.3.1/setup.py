# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyemerald']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyemerald',
    'version': '0.3.1',
    'description': '',
    'long_description': None,
    'author': 'matkvist',
    'author_email': 'bejsebakkevej@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
