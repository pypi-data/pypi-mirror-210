# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uquake',
 'uquake.core',
 'uquake.core.util',
 'uquake.grid',
 'uquake.imaging',
 'uquake.io',
 'uquake.io.event',
 'uquake.io.grid',
 'uquake.io.inventory',
 'uquake.io.waveform',
 'uquake.nlloc',
 'uquake.waveform']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.4,<4.0.0',
 'future>=0.18.2,<0.19.0',
 'h5py>=3.2.1,<4.0.0',
 'jedi==0.17.2',
 'loguru>=0.5.3,<0.6.0',
 'numpy>=1.18.0,<2.0.0',
 'obspy>=1.2.2,<2.0.0',
 'openpyxl>=3.0.6,<4.0.0',
 'pandas>=1.2.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyproj>=3.2.1,<4.0.0',
 'pyproject-toml>=0.0.10,<0.0.11',
 'pytest-asyncio>=0.21.0,<0.22.0',
 'pytest>=7.3.1,<8.0.0',
 'scikit-fmm>=2022.3.26,<2023.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'vtk>=9.0.1,<10.0.0']

entry_points = \
{'uquake.io.event': ['NLLOC = uquake.io.nlloc', 'QUAKEML = uquake.io.quakeml'],
 'uquake.io.grid': ['CSV = uquake.io.grid',
                    'NLLOC = uquake.io.grid',
                    'PICKLE = uquake.io.grid',
                    'VTK = uquake.io.grid'],
 'uquake.io.grid.CSV': ['readFormat = uquake.io.grid:read_csv',
                        'writeFormat = uquake.io.grid:write_csv'],
 'uquake.io.grid.NLLOC': ['readFormat = uquake.io.grid:read_nlloc'],
 'uquake.io.grid.PICKLE': ['readFormat = uquake.io.grid:read_pickle',
                           'writeFormat = uquake.io.grid:write_pickle'],
 'uquake.io.grid.VTK': ['readFormat = uquake.io.grid:read_vtk',
                        'writeFormat = uquake.io.grid:write_vtk'],
 'uquake.io.inventory': ['ESG_SENSOR = uquake.io.inventory'],
 'uquake.io.inventory.ESG_SENSOR': ['readFormat = '
                                    'uquake.io.inventory:read_esg_sensor_file'],
 'uquake.io.waveform': ['ESG_SEGY = uquake.io.waveform',
                        'HSF = uquake.io.waveform',
                        'IMS_ASCII = uquake.io.waveform',
                        'IMS_CONTINUOUS = uquake.io.waveform',
                        'TEXCEL_CSV = uquake.io.waveform'],
 'uquake.io.waveform.ESG_SEGY': ['readFormat = '
                                 'uquake.io.waveform:read_ESG_SEGY'],
 'uquake.io.waveform.IMS_ASCII': ['readFormat = '
                                  'uquake.io.waveform:read_IMS_ASCII'],
 'uquake.io.waveform.TEXCEL_CSV': ['readFormat = '
                                   'uquake.io.waveform:read_TEXCEL_CSV']}

setup_kwargs = {
    'name': 'uquake',
    'version': '1.3.0',
    'description': 'extension of the ObsPy library for local seismicity',
    'long_description': 'None',
    'author': 'uQuake development team',
    'author_email': 'dev@uQuake.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
