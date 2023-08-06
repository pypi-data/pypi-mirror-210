# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['timona']

package_data = \
{'': ['*']}

install_requires = \
['deepmerge', 'jinja2', 'pyyaml', 'requests']

entry_points = \
{'console_scripts': ['timona = timona.main:main']}

setup_kwargs = {
    'name': 'timona',
    'version': '0.0.2',
    'description': 'Tool to automate Helm deployments',
    'long_description': '# timona\n\nA tool to automate Helm deployments\n',
    'author': 'mihaiush',
    'author_email': 'mihaiush@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mihaiush/timona',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
