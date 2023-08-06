# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['report_ranger',
 'report_ranger.imports',
 'report_ranger.markdown_renderer',
 'report_ranger.output_formatter',
 'report_ranger.utils']

package_data = \
{'': ['*']}

install_requires = \
['argparse',
 'cerberus',
 'jinja2',
 'kaleido==0.2.1',
 'mistune',
 'num2words',
 'numpy',
 'openpyxl',
 'pandas',
 'plotly',
 'pyyaml',
 'tabulate',
 'watchdog']

setup_kwargs = {
    'name': 'report-ranger',
    'version': '2.0',
    'description': 'Create a report using markdown files.',
    'long_description': None,
    'author': 'Matthew Strahan',
    'author_email': 'matt@volkis.com.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
