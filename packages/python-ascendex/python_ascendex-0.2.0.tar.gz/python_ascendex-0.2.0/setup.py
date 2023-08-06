# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ascendex']

package_data = \
{'': ['*']}

install_requires = \
['aiosonic>=0.16.1,<0.17.0',
 'chardet>=4.0.0,<5.0.0',
 'ujson>=5.1.0,<6.0.0',
 'websockets>=11.0.2,<12']

setup_kwargs = {
    'name': 'python-ascendex',
    'version': '0.2.0',
    'description': 'Python API for AscendEx',
    'long_description': 'None',
    'author': 'Jan Skoda',
    'author_email': 'skoda@jskoda.cz',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
