# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beanie_batteries_queue']

package_data = \
{'': ['*']}

install_requires = \
['beanie>=1.19.1,<2.0.0']

setup_kwargs = {
    'name': 'beanie-batteries-queue',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Beanie Queue\n\nBeanie Queue is a simple queue system for Beanie (MongoDB). It allows you to create a queue of tasks to be processed by a worker.',
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
