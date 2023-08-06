# Nunchaku: Optimally partitioning data into piece-wise linear segments
`nunchaku` is a statistically rigorous, Bayesian algorithm to infer the optimal partitioning of a data set into contiguous piece-wise linear segments.

## Who might find this useful?
Scientists and engineers who are interested in regions where one variable depends linearly on the other within a 2D dataset.

## How does it work?
1. Given a 2D dataset, it infers the piece-wise linear description that best approximates the dataset.
2. It provides statistics for each linear segment, from which users select the segment(s) of most interest. 

## Installation
Type in Terminal (for Linux/Mac OS users) or Anaconda/Miniconda Prompt (for Windows users): 
```
> pip install nunchaku
```

For developers, create a virtual environment, install poetry and then install `nunchaku` with Poetry: 
```
> git clone https://git.ecdf.ed.ac.uk/s1856140/nunchaku.git
> cd nunchaku 
> poetry install --with dev 
```

## Quickstart
Data `x` is a list or a 1D Numpy array, sorted ascendingly; the data `y` is a list or a 1D Numpy array, or a 2D Numpy array with each row being one replicate of the measurement.
Below is a script to analyse the built-in example data. 
```
>>> from nunchaku import Nunchaku, get_example_data
>>> x, y = get_example_data()
>>> # load data and set the prior of the gradient
>>> nc = Nunchaku(x, y, prior=[-5,5]) 
>>> # compare models with 1, 2, 3 and 4 linear segments
>>> numseg, evidences = nc.get_number(max_num=4)
>>> # get the mean and standard deviation of the boundary points
>>> bds, bds_std = nc.get_iboundaries(numseg)
>>> # get the information of all segments
>>> info_df = nc.get_info(bds)
>>> # plot the data and the segments
>>> nc.plot(info_df)
```

## Documentation
Detailed documentation is available on [Readthedocs](https://nunchaku.readthedocs.io/en/latest/).

## Citation
A preprint on BioRxiv is coming soon.
