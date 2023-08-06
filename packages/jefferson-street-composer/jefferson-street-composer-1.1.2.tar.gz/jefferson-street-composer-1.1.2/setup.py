# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jefferson_street_composer',
 'jefferson_street_composer.services',
 'jefferson_street_composer.services.specifications']

package_data = \
{'': ['*']}

install_requires = \
['apache-airflow-providers-cncf-kubernetes==5.0.0',
 'apache-airflow==2.4.3',
 'google-cloud-orchestration-airflow==1.4.1']

setup_kwargs = {
    'name': 'jefferson-street-composer',
    'version': '1.1.2',
    'description': 'Library for Jefferson Street Technologies Composer Configuration',
    'long_description': '',
    'author': 'Nikolai McFall',
    'author_email': 'nikolai@jeffersonst.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
