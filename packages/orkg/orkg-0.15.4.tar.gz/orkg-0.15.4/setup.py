# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['orkg', 'orkg.client', 'orkg.client.templates', 'orkg.graph']

package_data = \
{'': ['*']}

install_requires = \
['Inflector>=3.1.0,<4.0.0',
 'cardinality>=0.1.1,<0.2.0',
 'hammock>=0.2.4,<0.3.0',
 'networkx>=3.1,<4.0',
 'pandas>=2.0.1,<3.0.0',
 'tqdm>=4.65.0,<5.0.0']

setup_kwargs = {
    'name': 'orkg',
    'version': '0.15.4',
    'description': 'The official python client for the Open Research Knowledge Graph (ORKG) API',
    'long_description': '# orkg-pypi\n[![Documentation Status](https://readthedocs.org/projects/orkg/badge/?version=latest)](https://orkg.readthedocs.io/en/latest/?badge=latest)\n[![PyPI version](https://badge.fury.io/py/orkg.svg)](https://badge.fury.io/py/orkg)\n\nA python client interacting with the ORKG API and sprinkling some python magic on top.\n\nThe package a implements many of the API calls described in the [documentation](http://tibhannover.gitlab.io/orkg/orkg-backend/api-doc/), and provides a set of extra features like graph pythonic objects and dynamic instantiation of entities from specifications.\n\nYou can find details about how-to use the package on [Read the Docs](https://orkg.readthedocs.io/en/latest/index.html).\n\nSpecial thanks to **Allard Oelen** , **Kheir Eddine Farfar**, and **Omar Arab Oghli** for their contributions to the code.',
    'author': 'Yaser Jaradeh',
    'author_email': 'yaser.jaradeh@tib.eu',
    'maintainer': 'Yaser Jaradeh',
    'maintainer_email': None,
    'url': 'http://orkg.org/about',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
