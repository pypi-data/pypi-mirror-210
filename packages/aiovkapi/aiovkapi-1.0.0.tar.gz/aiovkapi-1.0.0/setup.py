# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiovkapi']

package_data = \
{'': ['*']}

install_requires = \
['vkbottle>=4.3.12,<5.0.0']

setup_kwargs = {
    'name': 'aiovkapi',
    'version': '1.0.0',
    'description': '',
    'long_description': '',
    'author': 'FeeeeK',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
