# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['daskms',
 'daskms.apps',
 'daskms.apps.tests',
 'daskms.descriptors',
 'daskms.descriptors.tests',
 'daskms.experimental',
 'daskms.experimental.arrow',
 'daskms.experimental.arrow.tests',
 'daskms.experimental.zarr',
 'daskms.experimental.zarr.tests',
 'daskms.tests']

package_data = \
{'': ['*'], 'daskms.apps': ['conf/*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'dask[array]>=2023.1.0,<2024.0.0',
 'donfig>=0.7.0,<0.8.0',
 'python-casacore>=3.5.1,<4.0.0']

extras_require = \
{'arrow': ['pyarrow>=12.0.0,<13.0.0'],
 'complete': ['pyarrow>=12.0.0,<13.0.0',
              'zarr>=2.12.0,<3.0.0',
              'xarray>=2023.01.0,<2024.0.0',
              's3fs>=2023.1.0,<2024.0.0'],
 's3': ['s3fs>=2023.1.0,<2024.0.0'],
 'testing': ['minio>=7.1.11,<8.0.0', 'pytest>=7.1.3,<8.0.0'],
 'xarray': ['xarray>=2023.01.0,<2024.0.0'],
 'zarr': ['zarr>=2.12.0,<3.0.0']}

entry_points = \
{'console_scripts': ['dask-ms = daskms.apps.entrypoint:main']}

setup_kwargs = {
    'name': 'dask-ms',
    'version': '0.2.16',
    'description': 'xarray Dataset from CASA Tables',
    'long_description': '================================\nxarray Datasets from CASA Tables\n================================\n\n.. image:: https://img.shields.io/pypi/v/dask-ms.svg\n        :target: https://pypi.python.org/pypi/dask-ms\n\n.. image:: https://github.com/ratt-ru/dask-ms/actions/workflows/ci.yml/badge.svg\n        :target: https://github.com/ratt-ru/dask-ms/actions/workflows/ci.yml\n\n.. image:: https://readthedocs.org/projects/dask-ms/badge/?version=latest\n        :target: https://dask-ms.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\nConstructs xarray_ ``Datasets`` from CASA Tables via python-casacore_.\nThe ``Variables`` contained in the ``Dataset`` are dask_ arrays backed by\ndeferred calls to :code:`pyrap.tables.table.getcol`.\n\nSupports writing ``Variables`` back to the respective column in the Table.\n\nThe intention behind this package is to support the Measurement Set as\na data source and sink for the purposes of writing parallel, distributed\nRadio Astronomy algorithms.\n\nInstallation\n============\n\nTo install with xarray_ support:\n\n.. code-block:: bash\n\n  $ pip install dask-ms[xarray]\n\nWithout xarray_ similar, but reduced Dataset functionality is replicated\nin dask-ms itself. Expert users may wish to use this option to reduce\npython package dependencies.\n\n.. code-block:: bash\n\n  $ pip install dask-ms\n\n\nDocumentation\n=============\n\nhttps://dask-ms.readthedocs.io\n\nGitter Page\n===========\n\nhttps://gitter.im/dask-ms/community\n\nExample Usage\n=============\n\n\n.. code-block:: python\n\n    import dask.array as da\n    from daskms import xds_from_table, xds_to_table\n\n    # Create xarray datasets from Measurement Set "WSRT.MS"\n    ds = xds_from_table("WSRT.MS")\n    # Set the flag Variable on first Dataset to it\'s inverse\n    ds[0][\'flag\'] = (ds[0].flag.dims, da.logical_not(ds[0].flag))\n    # Write the flag column back to the Measurement Set\n    xds_to_table(ds, "WSRT.MS", "FLAG").compute()\n\n    print ds\n\n  [<xarray.Dataset>\n   Dimensions:         (chan: 64, corr: 4, row: 6552, uvw: 3)\n   Coordinates:\n       ROWID           (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n   Dimensions without coordinates: chan, corr, row, uvw\n   Data variables:\n       IMAGING_WEIGHT  (row, chan) float32 dask.array<shape=(6552, 64), chunksize=(6552, 64)>\n       ANTENNA1        (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       STATE_ID        (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       EXPOSURE        (row) float64 dask.array<shape=(6552,), chunksize=(6552,)>\n       MODEL_DATA      (row, chan, corr) complex64 dask.array<shape=(6552, 64, 4), chunksize=(6552, 64, 4)>\n       FLAG_ROW        (row) bool dask.array<shape=(6552,), chunksize=(6552,)>\n       CORRECTED_DATA  (row, chan, corr) complex64 dask.array<shape=(6552, 64, 4), chunksize=(6552, 64, 4)>\n       PROCESSOR_ID    (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       WEIGHT          (row, corr) float32 dask.array<shape=(6552, 4), chunksize=(6552, 4)>\n       FLAG            (row, chan, corr) bool dask.array<shape=(6552, 64, 4), chunksize=(6552, 64, 4)>\n       TIME            (row) float64 dask.array<shape=(6552,), chunksize=(6552,)>\n       SIGMA           (row, corr) float32 dask.array<shape=(6552, 4), chunksize=(6552, 4)>\n       SCAN_NUMBER     (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       INTERVAL        (row) float64 dask.array<shape=(6552,), chunksize=(6552,)>\n       OBSERVATION_ID  (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       TIME_CENTROID   (row) float64 dask.array<shape=(6552,), chunksize=(6552,)>\n       ARRAY_ID        (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       ANTENNA2        (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       DATA            (row, chan, corr) complex64 dask.array<shape=(6552, 64, 4), chunksize=(6552, 64, 4)>\n       FEED1           (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       FEED2           (row) int32 dask.array<shape=(6552,), chunksize=(6552,)>\n       UVW             (row, uvw) float64 dask.array<shape=(6552, 3), chunksize=(6552, 3)>\n   Attributes:\n       FIELD_ID:      0\n       DATA_DESC_ID:  0]\n\n-----------\nLimitations\n-----------\n\n1. Many Measurement Sets columns are defined as variably shaped,\n   but the actual data is fixed.\n   dask-ms_ will infer the shape of the\n   data from the first row and must be consistent\n   with that of other rows.\n   For example, this may be issue where multiple Spectral Windows\n   are present in the Measurement Set with differing channels\n   per SPW.\n\n   dask-ms_ works around this by partitioning the\n   Measurement Set into multiple datasets.\n   The first row\'s shape is used to infer the shape of the partition.\n   Thus, in the case of multiple Spectral Window\'s, we can partition\n   the Measurement Set by DATA_DESC_ID to create a dataset for\n   each Spectral Window.\n\n.. _dask: https://dask.pydata.org\n.. _dask-ms: https://github.com/ska-sa/dask-ms\n.. _xarray: https://xarray.pydata.org\n.. _python-casacore: https://github.com/casacore/python-casacore\n',
    'author': 'Simon Perkins',
    'author_email': 'simon.perkins@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
