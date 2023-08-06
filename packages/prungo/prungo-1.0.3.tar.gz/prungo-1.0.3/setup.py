# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prungo']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.10.8,<2.0.0']

setup_kwargs = {
    'name': 'prungo',
    'version': '1.0.3',
    'description': 'A package for basic utility functions/classes',
    'long_description': '# prungo-util\nutility package for importing into projects\n',
    'author': 'c-prungo',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/c-prungo/prungo-util',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
