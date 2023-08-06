# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dimm_utils']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.26.138,<2.0.0']

setup_kwargs = {
    'name': 'dimm-utils',
    'version': '0.1.1',
    'description': 'A collection of utilities for DIMM',
    'long_description': '## How to publish\n\n> Manually for now to pypi via api key\n\n- poetry build\n- poetry publish\n',
    'author': 'Eric Juta',
    'author_email': 'ericjuta@trisolaris.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
