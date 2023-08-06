# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dionpy', 'dionpy.modules']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=5.0.2,<6.0.0',
 'echaim>=1.0.8,<2.0.0',
 'ffmpeg-progress-yield>=0.3.0,<0.4.0',
 'h5py>=3.7.0,<4.0.0',
 'healpy>=1.16.1,<2.0.0',
 'iricore>=1.4.1,<2.0.0',
 'it>=1.0.0,<2.0.0',
 'matplotlib>=3.6.0,<4.0.0',
 'numpy>=1.22,<2.0',
 'pymap3d>=3.0.1,<4.0.0',
 'pytz>=2022.1,<2023.0',
 'scipy>=1.9.3,<2.0.0',
 'setuptools>=67.6.1,<68.0.0',
 'sphinx-autodoc-typehints>=1.19.1,<2.0.0',
 'sphinx-rtd-theme>=1.0.0,<2.0.0',
 'sphinxcontrib-bibtex>=2.5.0,<3.0.0',
 'tqdm>=4.64.1,<5.0.0']

setup_kwargs = {
    'name': 'dionpy',
    'version': '0.99.8',
    'description': 'Dynamic ionosphere model for global 21 cm experiments',
    'long_description': '[//]: # (![]&#40;docs/images/logos/logo_wide.png&#41;)\n\n# DIonPy\nThe `dionpy` package provides model of ionosphere refraction and attenuation based on the \n[IRI2020 Ionosphere Model](https://irimodel.org/).\n\nMore details are available at our [documentation page](https://dionpy.readthedocs.io/en/latest/).',
    'author': 'Vadym Bidula',
    'author_email': 'vadym.bidula@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/lap1dem/dionpy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
