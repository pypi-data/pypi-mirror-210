# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sayql']

package_data = \
{'': ['*']}

install_requires = \
['duckdb>=0.8.0,<0.9.0',
 'langchain>=0.0.179,<0.0.180',
 'openai>=0.27.7,<0.28.0',
 'pandas>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'sayql',
    'version': '0.1.1',
    'description': 'Talk to your data',
    'long_description': None,
    'author': 'Ryan',
    'author_email': 'ryan.sudhakaran@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
