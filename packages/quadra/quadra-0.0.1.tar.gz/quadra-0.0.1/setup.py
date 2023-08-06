# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quadra']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'quadra',
    'version': '0.0.1',
    'description': 'Deep Learning experiment orchestration tool',
    'long_description': '# Deep Learning experiment orchestration tool',
    'author': 'rcmalli',
    'author_email': 'refikcanmalli@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
