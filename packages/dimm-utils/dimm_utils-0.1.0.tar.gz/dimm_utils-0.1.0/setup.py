# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dimm_utils']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['dimm_utils = dimm_utils.core:main']}

setup_kwargs = {
    'name': 'dimm-utils',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Eric Juta',
    'author_email': 'ericjuta@trisolaris.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
