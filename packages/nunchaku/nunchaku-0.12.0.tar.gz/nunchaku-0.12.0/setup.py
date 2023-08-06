# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nunchaku']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.0,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.4,<2.0',
 'scipy>=1.7.3,<2.0.0',
 'sympy>=1.9,<2.0',
 'tqdm>=4.65.0,<5.0.0']

setup_kwargs = {
    'name': 'nunchaku',
    'version': '0.12.0',
    'description': 'Optimally partitioning data into piece-wise linear segments.',
    'long_description': '# Nunchaku: Optimally partitioning data into piece-wise linear segments\n`nunchaku` is a statistically rigorous, Bayesian algorithm to infer the optimal partitioning of a data set into contiguous piece-wise linear segments.\n\n## Who might find this useful?\nScientists and engineers who are interested in regions where one variable depends linearly on the other within a 2D dataset.\n\n## How does it work?\n1. Given a 2D dataset, it infers the piece-wise linear description that best approximates the dataset.\n2. It provides statistics for each linear segment, from which users select the segment(s) of most interest. \n\n## Installation\nType in Terminal (for Linux/Mac OS users) or Anaconda/Miniconda Prompt (for Windows users): \n```\n> pip install nunchaku\n```\n\nFor developers, create a virtual environment, install poetry and then install `nunchaku` with Poetry: \n```\n> git clone https://git.ecdf.ed.ac.uk/s1856140/nunchaku.git\n> cd nunchaku \n> poetry install --with dev \n```\n\n## Quickstart\nData `x` is a list or a 1D Numpy array, sorted ascendingly; the data `y` is a list or a 1D Numpy array, or a 2D Numpy array with each row being one replicate of the measurement.\nBelow is a script to analyse the built-in example data. \n```\n>>> from nunchaku import Nunchaku, get_example_data\n>>> x, y = get_example_data()\n>>> # load data and set the prior of the gradient\n>>> nc = Nunchaku(x, y, prior=[-5,5]) \n>>> # compare models with 1, 2, 3 and 4 linear segments\n>>> numseg, evidences = nc.get_number(max_num=4)\n>>> # get the mean and standard deviation of the boundary points\n>>> bds, bds_std = nc.get_iboundaries(numseg)\n>>> # get the information of all segments\n>>> info_df = nc.get_info(bds)\n>>> # plot the data and the segments\n>>> nc.plot(info_df)\n```\n\n## Documentation\nDetailed documentation is available on [Readthedocs](https://nunchaku.readthedocs.io/en/latest/).\n\n## Citation\nA preprint on BioRxiv is coming soon.\n',
    'author': 'Yu Huo',
    'author_email': 'yu.huo@ed.ac.uk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://nunchaku.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
