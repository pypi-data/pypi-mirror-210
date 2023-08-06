# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gravitas']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.2,<2.0.0']

setup_kwargs = {
    'name': 'gravitas',
    'version': '0.0.9',
    'description': 'High-fidelity gravity fields for satellite propagation',
    'long_description': 'test',
    'author': 'Liam Robinson',
    'author_email': 'robin502@purdue.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
