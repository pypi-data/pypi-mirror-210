# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['valphi']

package_data = \
{'': ['*']}

install_requires = \
['distlib>=0.3.6,<0.4.0', 'dumbo-asp>=0.0.37,<0.0.38', 'pydot>=1.4.2,<2.0.0']

setup_kwargs = {
    'name': 'valphi',
    'version': '0.3.34',
    'description': 'Logic programs ralying on ValPhi semantics',
    'long_description': 'None',
    'author': 'Mario Alviano',
    'author_email': 'mario.alviano@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
