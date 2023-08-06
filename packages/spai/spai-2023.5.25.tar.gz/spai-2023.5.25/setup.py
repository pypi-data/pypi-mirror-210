# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spai',
 'spai.cli',
 'spai.cli.commands',
 'spai.data',
 'spai.data.satellite',
 'spai.data.satellite.sentinelhub',
 'spai.image',
 'spai.storage']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'spai',
    'version': '2023.5.25',
    'description': '',
    'long_description': '',
    'author': 'Juan Sensio',
    'author_email': 'it@earthpulse.es',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
