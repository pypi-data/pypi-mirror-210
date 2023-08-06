# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dicomindex']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=2.0.10,<3.0.0',
 'click>=8.1.3,<9.0.0',
 'pydicom>=2.3.1,<3.0.0',
 'tabulate>=0.9.0,<0.10.0',
 'tqdm>=4.65.0,<5.0.0']

entry_points = \
{'console_scripts': ['dicomindex = dicomindex.cli:main']}

setup_kwargs = {
    'name': 'dicomindex',
    'version': '0.2.7',
    'description': 'Index dicom files into patient->study->series->instance',
    'long_description': None,
    'author': 'sjoerdk',
    'author_email': 'sjoerd.kerkstra@radboudumc.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
