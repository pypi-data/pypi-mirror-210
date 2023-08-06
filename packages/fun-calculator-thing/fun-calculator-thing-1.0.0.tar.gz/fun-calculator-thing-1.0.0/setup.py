# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fun_calculator_thing']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fun-calculator-thing',
    'version': '1.0.0',
    'description': 'A bunch of calculator functions',
    'long_description': None,
    'author': 'Luca Simpson',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
