# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['refaci']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]', 'typing-extensions']

entry_points = \
{'console_scripts': ['refaci = refaci.__main__:app']}

setup_kwargs = {
    'name': 'refaci',
    'version': '0.1.0',
    'description': '',
    'long_description': '# refaci\n\nA toolbox for changing imports in enormous codebases after a large refactoring.\n\n---\n\n<p align="center">\n<a href="https://github.com/ovsyanka83/refaci/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/Ovsyanka83/refaci/actions/workflows/test.yaml/badge.svg?branch=main&event=push" alt="Test">\n</a>\n<a href="https://codecov.io/gh/ovsyanka83/refaci" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/ovsyanka83/refaci?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/refaci/" target="_blank">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/refaci?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/refaci/" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/refaci?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n## Installation\n\n```bash\npip install refaci\n```\n',
    'author': 'Stanislav Zmiev',
    'author_email': 'szmiev2000@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/ovsyanka83/refaci',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
