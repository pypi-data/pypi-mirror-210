# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rocks']

package_data = \
{'': ['*']}

install_requires = \
['Levenshtein>=0.16.0',
 'aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.8.2',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'click>=8.1.2',
 'faust-cchardet>=2.1.7',
 'furo>=2022.9.15,<2023.0.0',
 'matplotlib>=3.4.3',
 'nest-asyncio>=1.5.1,<2.0.0',
 'numpy>=1.21',
 'pandas>=1.3.5',
 'platformdirs>=2.6.2,<3.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'rapidfuzz>=3,<4',
 'requests>=2.26.0,<3.0.0',
 'rich>=12.2.0',
 'sphinx-copybutton>=0.5.0,<0.6.0',
 'sphinx_design>=0.3.0,<0.4.0']

entry_points = \
{'console_scripts': ['rocks = rocks.cli:cli_rocks']}

setup_kwargs = {
    'name': 'space-rocks',
    'version': '1.8.0',
    'description': 'Python client for SsODNet data access.',
    'long_description': '<p align="center">\n  <img width="260" src="https://raw.githubusercontent.com/maxmahlke/rocks/master/docs/_static/logo_rocks.svg">\n</p>\n\n<p align="center">\n  <a href="https://github.com/maxmahlke/rocks#features"> Features </a> - <a href="https://github.com/maxmahlke/rocks#install"> Install </a> - <a href="https://github.com/maxmahlke/rocks#documentation"> Documentation </a>\n</p>\n\n<br>\n\n<div align="center">\n  <a href="https://img.shields.io/pypi/pyversions/space-rocks">\n    <img src="https://img.shields.io/pypi/pyversions/space-rocks"/>\n  </a>\n  <a href="https://img.shields.io/pypi/v/space-rocks">\n    <img src="https://img.shields.io/pypi/v/space-rocks"/>\n  </a>\n  <a href="https://readthedocs.org/projects/rocks/badge/?version=latest">\n    <img src="https://readthedocs.org/projects/rocks/badge/?version=latest"/>\n  </a>\n  <a href="https://arxiv.org/abs/2209.10697">\n    <img src="https://img.shields.io/badge/arXiv-2209.10697-f9f107.svg"/>\n  </a>\n</div>\n\n<br>\n\n## Features\n\nExplore asteroid data on the command-line...\n\n``` sh\n$ rocks id 221\n(221) Eos\n\n$ rocks class Eos\nMB>Outer\n\n$ rocks albedo Eos\n0.136 +- 0.004\n\n$ rocks taxonomy Eos\nK\n\n$ rocks density Eos\n4.559e+03 +- 1.139e+03 kg/m$^3$\n```\n\n... and in a `python` script.\n\n``` python\n>>> import rocks\n>>> rocks.identify("1902ug")\n(\'Fortuna\', 19)\n>>> ceres = rocks.Rock("ceres")\n>>> ceres.diameter.value\n848.4\n>>> ceres.diameter.unit\n\'km\'\n>>> ceres.mass.value\n9.384e+20\n>>> ceres.mass.error\n6.711e+17\n```\n\n## Install\n\nInstall from PyPi using `pip`:\n\n     $ pip install space-rocks\n\nThe minimum required `python` version is 3.7.\n\n\n## Documentation\n\nCheck out the documentation at [rocks.readthedocs.io](https://rocks.readthedocs.io/en/latest/) or run\n\n     $ rocks docs\n',
    'author': 'Max Mahlke',
    'author_email': 'max.mahlke@oca.eu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://rocks.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.12',
}


setup(**setup_kwargs)
