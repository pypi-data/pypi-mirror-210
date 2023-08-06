# STARRED: STARlet REgularized Deconvolution 

[![pipeline status](https://gitlab.com/cosmograil/starred/badges/main/pipeline.svg)](https://gitlab.com/cosmograil/starred/commits/main)
[![coverage report](https://gitlab.com/cosmograil/starred/badges/main/coverage.svg)](https://cosmograil.gitlab.io/starred/coverage/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.05340/status.svg)](https://doi.org/10.21105/joss.05340)


STARlet REgularized Deconvolution (STARRED) is a Python deconvolution method powered by Starlet regularization and JAX automatic differentiation. It uses a Point Spread Function (PSF) narrower than the original one as kernel. 

## Installation 

### Through PyPI

STARRED releases are distributed through the Python Package Index (PyPI). To install the latest version use `pip`:

```bash
$ pip install starred-astro
```

STARRED runs much faster on GPUs, so make sure you install a version of JAX that is compatible 
with your version of CUDA and cuDNN: 
``` bash 
$ pip install "jax[cuda11_cudnn86]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```

## Requirements 

STARRED requires the following Python packages:

* `astropy`

* `dill`

* `jax`

* `jaxlib`

* `jaxopt`

* `matplotlib`

* `numpy`

* `scikit-image`

* `scipy`

* `optax`

* `tqdm`
    


## Example Notebooks and Documentation
The full documentation can be found [here](https://cosmograil.gitlab.io/starred/). 

Example notebooks are located in the [notebooks](https://gitlab.com/cosmograil/starred/-/tree/main/notebooks) folder: 

* [Ground-based narrow PSF generation](https://gitlab.com/cosmograil/starred/-/blob/main/notebooks/1_WFI%20narrow%20PSF%20generation.ipynb)

* [Ground-based joint deconvolution](https://gitlab.com/cosmograil/starred/-/blob/main/notebooks/2_DESJ0602-4335%20joint%20deconvolution.ipynb)

* [Another ground-based joint deconvolution](https://gitlab.com/cosmograil/starred/-/blob/main/notebooks/3_Another%20lensed%20quasar%20-%20joint%20deconvolution.ipynb)

* [JWST PSF generation and deconvolution](https://gitlab.com/cosmograil/starred/-/blob/main/notebooks/4_JWST%20deconvolution.ipynb)

* [DES2038 joint deconvolution](https://gitlab.com/cosmograil/starred/-/blob/main/notebooks/5_DES2038_from_WFI_joint_deconvolution.ipynb)

* [HST PSF reconstruction](https://gitlab.com/cosmograil/starred/-/blob/main/notebooks/6_HST-PSF%20reconstruction.ipynb)

## Attribution

If you use this code, please cite [Michalewicz et al. 2023](https://joss.theoj.org/papers/10.21105/joss.05340) as indicated in the [documentation](https://cosmograil.gitlab.io/starred/citing.html).

## License
STARRED is a free software. You can redistribute it and/or modify it under the terms of the 
GNU General Public License as published by the Free Software Foundation.

STARRED is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY, without 
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
General Public License for more details ([LICENSE.txt](LICENSE)).
