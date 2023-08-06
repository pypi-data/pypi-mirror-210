# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webknossos',
 'webknossos._nml',
 'webknossos.administration',
 'webknossos.annotation',
 'webknossos.client',
 'webknossos.client._generated',
 'webknossos.client._generated.api',
 'webknossos.client._generated.api.datastore',
 'webknossos.client._generated.api.default',
 'webknossos.client._generated.models',
 'webknossos.client._resumable',
 'webknossos.dataset',
 'webknossos.dataset._utils',
 'webknossos.dataset._utils.vendor',
 'webknossos.geometry',
 'webknossos.skeleton']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'attrs>=22.1.0,<23.0.0',
 'boltons>=21.0.0,<21.1.0',
 'cattrs>=22.2.0,<23.0.0',
 'cluster_tools==0.12.4',
 'fsspec>=2022.2.0,<2023.0.0',
 'httpx>=0.15.4,<0.19.0',
 'loxun>=2.0,<3.0',
 'natsort>=6.2.0,<7.0.0',
 'networkx>=2.6.2,<3.0.0',
 'numcodecs>=0.10,<0.11',
 'numpy>=1.21.0,<2.0.0',
 'psutil>=5.6.7,<6.0.0',
 'python-dateutil>=2.8.0,<3.0.0',
 'python-dotenv>=0.19.0,<0.20.0',
 'rich>=10.9.0,<11.0.0',
 'scikit-image>=0.19.3,<0.20.0',
 'scipy>=1.9.0,<2.0.0',
 'typing-extensions>=4.0,<5.0',
 'universal-pathlib==0.0.19',
 'wkw==1.1.18',
 'zarr>=2.14.0,<3.0.0',
 'zipp>=3.5.0,<4.0.0']

extras_require = \
{'all': ['imagecodecs>=2021.11.20',
         'JPype1>=1.3.0,<2.0.0',
         'pims>=0.6.0,<0.7.0',
         'tifffile>=2021.11.2',
         'pylibCZIrw>=3.2,<4.0'],
 'bioformats': ['JPype1>=1.3.0,<2.0.0', 'pims>=0.6.0,<0.7.0'],
 'czi': ['pims>=0.6.0,<0.7.0', 'pylibCZIrw>=3.2,<4.0'],
 'imagecodecs': ['imagecodecs>=2021.11.20', 'pims>=0.6.0,<0.7.0'],
 'pims': ['pims>=0.6.0,<0.7.0'],
 'tifffile': ['pims>=0.6.0,<0.7.0', 'tifffile>=2021.11.2']}

setup_kwargs = {
    'name': 'webknossos',
    'version': '0.12.4',
    'description': 'Python API for working with WEBKNOSSOS datasets, annotations, and for WEBKNOSSOS server interaction.',
    'long_description': "# WEBKNOSSOS Python Library\n[![PyPI version](https://img.shields.io/pypi/v/webknossos)](https://pypi.python.org/pypi/webknossos)\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/webknossos.svg)](https://pypi.python.org/pypi/webknossos)\n[![Build Status](https://img.shields.io/github/actions/workflow/status/scalableminds/webknossos-libs/.github/workflows/ci.yml?branch=master)](https://github.com/scalableminds/webknossos-libs/actions?query=workflow%3A%22CI%22)\n[![Documentation](https://img.shields.io/badge/docs-passing-brightgreen.svg)](https://docs.webknossos.org/webknossos-py)\n[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nPython API for working with [WEBKNOSSOS](https://webknossos.org) datasets, annotations, and for WEBKNOSSOS server interaction.\n\nFor the WEBKNOSSOS server, please refer to https://github.com/scalableminds/webknossos.\n\n## Features\n\n- easy-to-use dataset API for reading/writing/editing raw 2D/3D image data and volume annotations/segmentation in WEBKNOSSOS wrap (*.wkw) format\n    - add/remove layers\n    - update metadata (`datasource-properties.json`) \n    - up/downsample layers\n    - compress layers \n    - add/remove magnifications\n    - execute any of the `wkCuber` operations from your code\n- manipulation of WEBKNOSSOS skeleton annotations (*.nml) as Python objects\n    - access to nodes, comments, trees, bounding boxes, metadata, etc.\n    - create new skeleton annotation from Graph structures or Python objects\n- interaction, connection & scripting with your WEBKNOSSOS instance over the REST API\n    - up- & downloading annotations and datasets\n\nPlease refer to [the documentation for further instructions](https://docs.webknossos.org/webknossos-py).\n\n## Installation\nThe `webknossos` package requires at least Python 3.8.\n\nYou can install it from [pypi](https://pypi.org/project/webknossos/), e.g. via pip:\n\n```bash\npip install webknossos\n```\n\n## Examples\nSee the [examples folder](examples) or the [the documentation](https://docs.webknossos.org/webknossos-py).\n\n## Contributions & Development\nPlease see the [respective documentation page](https://docs.webknossos.org/webknossos-py/development.html).\n\n## License\n[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html)\nCopyright [scalable minds](https://scalableminds.com)\n\n## Test Data Credits\nExcerpts for testing purposes have been sampled from:\n\n* Dow Jacobo Hossain Siletti Hudspeth (2018). **Connectomics of the zebrafish's lateral-line neuromast reveals wiring and miswiring in a simple microcircuit.** eLife. [DOI:10.7554/eLife.33988](https://elifesciences.org/articles/33988)\n* Zheng Lauritzen Perlman Robinson Nichols Milkie Torrens Price Fisher Sharifi Calle-Schuler Kmecova Ali Karsh Trautman Bogovic Hanslovsky Jefferis Kazhdan Khairy Saalfeld Fetter Bock (2018). **A Complete Electron Microscopy Volume of the Brain of Adult Drosophila melanogaster.** Cell. [DOI:10.1016/j.cell.2018.06.019](https://www.cell.com/cell/fulltext/S0092-8674(18)30787-6). License: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)\n* Bosch Ackels Pacureanu et al (2022). **Functional and multiscale 3D structural investigation of brain tissue through correlative in vivo physiology, synchrotron microtomography and volume electron microscopy.** Nature Communications. [DOI:10.1038/s41467-022-30199-6](https://www.nature.com/articles/s41467-022-30199-6)\n",
    'author': 'scalable minds',
    'author_email': 'hello@scalableminds.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://docs.webknossos.org/webknossos-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
