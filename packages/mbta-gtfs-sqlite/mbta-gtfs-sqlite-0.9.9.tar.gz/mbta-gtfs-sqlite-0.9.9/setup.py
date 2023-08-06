# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mbta_gtfs_sqlite', 'mbta_gtfs_sqlite.models', 'mbta_gtfs_sqlite.utils']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=2.0.7,<3.0.0', 'requests>=2.28.2,<3.0.0']

setup_kwargs = {
    'name': 'mbta-gtfs-sqlite',
    'version': '0.9.9',
    'description': "Query the MBTA's static GTFS feeds using sqlite",
    'long_description': None,
    'author': 'Ian Reynolds',
    'author_email': 'ireynolds@transitmatters.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
