# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modshib', 'modshib.migrations']

package_data = \
{'': ['*'], 'modshib': ['templates/registration/*']}

install_requires = \
['Django>=4.0', 'django-auth-cli-certic>=0.1.3,<0.2.0']

setup_kwargs = {
    'name': 'django-modshib-certic',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mickaël Desfrênes',
    'author_email': 'mickael.desfrenes@unicaen.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.certic.unicaen.fr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
