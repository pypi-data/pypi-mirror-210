# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pickled_carrots', 'pickled_carrots.vinegar', 'pickled_carrots.vinegar.tests']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=2.0.13,<3.0.0',
 'boto3>=1.26.128,<2.0.0',
 'certifi>=2022.12.7,<2023.0.0',
 'cryptography>=40.0.2,<41.0.0',
 'h5py>=3.8.0,<4.0.0',
 'ipdb>=0.13.13,<0.14.0',
 'jupyter>=1.0.0,<2.0.0',
 'mplstereonet>=0.6.2,<0.7.0',
 'plotly>=5.14.1,<6.0.0',
 'psutil>=5.9.5,<6.0.0',
 'pymongo>=4.3.3,<5.0.0',
 'pyodbc==4.0.34',
 'pyproj==3.4.1',
 'python-ternary>=1.0.8,<2.0.0',
 'pytz>=2023.3,<2024.0',
 'shapely>=2.0.1,<3.0.0',
 'statsmodels>=0.14.0,<0.15.0',
 'uquake>=1.2.4,<2.0.0']

setup_kwargs = {
    'name': 'pickled-carrots',
    'version': '0.1.7',
    'description': '',
    'long_description': "# ESG_Research\n\nThis repository contains Python and C# code which is used for various different functions. In this document we will go through what each folder contains.\n\n__Analytics_Notebooks__\n\nThis folder contains Jupyter notebooks which have various different functionalities. More notebooks can be found on the DataShare, under Frac4/Notebooks.\n\n&nbsp;\n\n\n__ESG-dash__\n\nA dash-based dashboard for evaluating sensor quality for mining sites.\n\n&nbsp;\n\n\n__ESG__\n\nThe main module folder for our Python codes. The files within this folder are used in most of our jupyter notebooks. More details on what each file contains can be found in the folder.\n\n&nbsp;\n\n__ITG-FMC__\n\nContains the tiltmeter processing dashboard written in Python, a Fiber processing C# app, a DPA and DPA-RTA C# app, and a copy of the Stress Inversion python package (which has since been merged into the main ESG repo.\n\n&nbsp;\n\n__Scripts__\n\nContains various Python scripts which are used to automated processes such as HypoDD or noise analysis.\n\n&nbsp;\n\n__build/lib, dist, esg_das, esg_dts__\n\nPython code for processing Fiber data. \n\n&nbsp;\n\n__Miscellaneous__\n\nThere are some additional files in this folder which are related to replicated anaconda environments. The requirements.txt file can be used to create ESG's default environment.\n",
    'author': 'pickled cattots team',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
