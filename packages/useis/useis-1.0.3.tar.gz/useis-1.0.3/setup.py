# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['useis',
 'useis.ai',
 'useis.clients',
 'useis.core',
 'useis.examples.classifier',
 'useis.examples.picker',
 'useis.processors',
 'useis.sandbox',
 'useis.sandbox.ai_picker',
 'useis.sandbox.demo_kafka',
 'useis.sandbox.event_classification',
 'useis.sandbox.event_classification.inventory',
 'useis.sandbox.tomography',
 'useis.scripts',
 'useis.scripts.ai',
 'useis.services',
 'useis.services.file_server',
 'useis.services.grid',
 'useis.services.models',
 'useis.settings',
 'useis.tomography']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.4,<4.0.0',
 'fastapi>=0.68.1,<0.69.0',
 'furl>=2.1.2,<3.0.0',
 'myst-parser>=0.15.1,<0.16.0',
 'numpy>=1.3.0,<2.0.0',
 'pillow>=9.4.0,<10.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyproj==3.4.1',
 'python-multipart>=0.0.5,<0.0.6',
 'rinohtype>=0.5.3,<0.6.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'uquake>=1.2.4,<2.0.0',
 'uvicorn>=0.15.0,<0.16.0']

extras_require = \
{':extra == "docs"': ['Sphinx>=4.1.2,<5.0.0', 'sphinx-rtd-theme>=0.5.2,<0.6.0']}

entry_points = \
{'console_scripts': ['grid_service = useis.services.grid.server:start']}

setup_kwargs = {
    'name': 'useis',
    'version': '1.0.3',
    'description': '',
    'long_description': 'None',
    'author': 'jpmercier',
    'author_email': 'jpmercier01@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
