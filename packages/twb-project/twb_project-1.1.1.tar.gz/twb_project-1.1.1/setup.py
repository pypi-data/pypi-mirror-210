# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['twb']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.12.2,<5.0.0',
 'jsonlines>=3.1.0,<4.0.0',
 'psutil>=5.9.5,<6.0.0',
 'py7zr>=0.20.5,<0.21.0',
 'requests>=2.31.0,<3.0.0',
 'tqdm>=4.65.0,<5.0.0',
 'xmltodict>=0.13.0,<0.14.0',
 'zstandard>=0.21.0,<0.22.0']

entry_points = \
{'console_scripts': ['benchmark = tests.benchmark:main']}

setup_kwargs = {
    'name': 'twb-project',
    'version': '1.1.1',
    'description': 'An unified tool for the research in extracting information from Wikipedia Edit History chunk.',
    'long_description': '<img src="https://imagedelivery.net/Dr98IMl5gQ9tPkFM5JRcng/007bbe1a-fc2b-4135-e9a6-0d8784004c00/HD" alt="TWB" />\n\n# Temporal Wikipedia Blocks (TWB)\n\nTemporal Wikipedia Blocks (TWB) is a powerful Python package designed to process the extensive edit history of Wikipedia pages into easily manageable and memory-friendly blocks. The package is specifically developed to enable efficient parallelization and composition of these blocks to facilitate faster processing and analysis of large Wikipedia datasets. The original design of this package is to build other Wikipedia-oriented datasets on top of it.\n\nThe package works by dividing the Wikipedia edit history into temporal blocks, which are essentially subsets of the complete dataset that are based on time intervals. These blocks can then be easily processed and analyzed without the need to load the entire dataset into memory.\n\n## Installation\n\nThe package is available on PyPI and can be installed using pip:\n\n```bash\npip install twb-project\n```\n\n## Benefits\n\n- **Efficient**: The package is designed to be memory-friendly and can be easily parallelized to process large datasets.\n- **Fast**: The package is designed to be fast and can be easily optimized to process large datasets.\n- **Flexible**: The package is designed to be flexible and can be easily extended to support other types of blocks.\n- **Composable**: The package is designed to be composable and can be easily combined with other packages to build other datasets.\n\n## Specification\n\n- Default compression method: ZStandard.\n',
    'author': 'Lingxi Li',
    'author_email': 'hi@lingxi.li',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://twb.lingxi.li/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
