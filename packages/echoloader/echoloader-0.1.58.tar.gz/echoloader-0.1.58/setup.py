# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['echoloader']

package_data = \
{'': ['*']}

install_requires = \
['imageio-ffmpeg==0.4.3',
 'imageio==2.9.0',
 'numpy==1.23.5',
 'opencv-python>=4.5.5.64,<5.0.0.0',
 'pathy>=0.10.1,<0.11.0',
 'pydicom>=2.3.0,<3.0.0',
 'pynetdicom>=1.5.7,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-gdcm>=3.0.12,<4.0.0',
 'requests>=2.27.1,<3.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'watchdog>=2.1.7,<3.0.0']

entry_points = \
{'console_scripts': ['echoloader = echoloader.watcher:main']}

setup_kwargs = {
    'name': 'echoloader',
    'version': '0.1.58',
    'description': '',
    'long_description': 'None',
    'author': 'mathias',
    'author_email': 'mathias@us2.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
