# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dumbo_utils']

package_data = \
{'': ['*']}

install_requires = \
['distlib>=0.3.6,<0.4.0',
 'rich>=13.3.1,<14.0.0',
 'typeguard>=4.0.0,<5.0.0',
 'typer>=0.9.0,<0.10.0',
 'valid8>=5.1.2,<6.0.0']

setup_kwargs = {
    'name': 'dumbo-utils',
    'version': '0.1.9',
    'description': 'Different utilities to be reused in other projects',
    'long_description': '# dumbo-utils\n\nDifferent utilities to be reused in other projects\n\n\n# Prerequisites\n\n- Python 3.10+\n\n\n\n## Install\n\nAdd to your project with\n```bash\n$ poetry add dumbo-utils\n```',
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
