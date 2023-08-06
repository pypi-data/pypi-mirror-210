# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite', 'cognite.cdffs']

package_data = \
{'': ['*']}

install_requires = \
['cognite-sdk>=6.1.10,<7.0.0',
 'fsspec>=2023.5.0,<2024.0.0',
 'pydantic>=1.10.8,<2.0.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'requests>=2.31.0,<3.0.0',
 'twine>=4.0.2,<5.0.0']

setup_kwargs = {
    'name': 'cognite-cdffs',
    'version': '0.2.3',
    'description': 'File System Interface for CDF Files',
    'long_description': '<a href="https://cognite.com/">\n  <img alt="Cognite" src="https://raw.githubusercontent.com/cognitedata/cognite-python-docs/master/img/cognite_logo_black.png" alt="Cognite logo" title="Cognite" align="right" height="80">\n</a>\n\n[![GitHub](https://img.shields.io/github/license/cognitedata/cdffs)](https://github.com/cognitedata/cdffs/blob/main/LICENSE)\n[![Documentation Status](https://readthedocs.org/projects/cdffs/badge/?version=latest)](https://cdffs.readthedocs.io/en/latest/?badge=latest)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![codecov](https://codecov.io/gh/cognitedata/cdffs/branch/main/graph/badge.svg)](https://codecov.io/gh/cognitedata/cdffs)\n![PyPI](https://img.shields.io/pypi/v/cognite-cdffs)\n\n# cdffs\n\nA file system interface (`cdffs`) to allow users to work with CDF Files using the [fsspec](https://filesystem-spec.readthedocs.io/en/latest/) supported/compatible python packages (`pandas`, `xarray` etc).\n\n`fsspec` provides an abstract file system interface to work with local/cloud storages and based on the protocol name (example, `s3` or `abfs`) provided in the path, `fsspec` translates the incoming requests to storage specific implementations and send the responses back to the upstream package to work with the desired data.\n\nRefer [fsspec documentation](https://filesystem-spec.readthedocs.io/en/latest/#who-uses-fsspec) to get the list of all supported/compatible python packages.\n\n## Installation\n\n`cdffs` is available on PyPI. Install using,\n\n```shell\npip install cognite-cdffs\n```\n\n## Usage\n\nImportant steps to follow when working with CDF Files using the `fsspec` supported python packages.\n\n1) Import `cdffs` package\n```python\n  from cognite import cdffs  # noqa\n```\n\n2) Follow instructions from [Authentication](https://cdffs.readthedocs.io/en/latest/authentication.html) to authenticate.\n\n3) Read/write the files from/to CDF using `fsspec` supported packages. Example,\n\n    * Read `zarr` files using using `xarray`.\n\n    ```python\n    ds = xarray.open_zarr("cdffs://sample_data/test.zarr")\n    ```\n    * Write `zarr` files using `xarray`.\n\n    ```python\n    ds.to_zarr("cdffs://sample_data/test.zarr", storage_options={"file_metadata": metadata})\n    ```\n\nRefer [cdffs.readthedocs.io](https://cdffs.readthedocs.io) for more details.\n\n## Contributing\nWant to contribute? Check out [CONTRIBUTING](CONTRIBUTING.md).\n',
    'author': 'Infant Alex',
    'author_email': 'infant.alex@cognite.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.10,<4.0.0',
}


setup(**setup_kwargs)
