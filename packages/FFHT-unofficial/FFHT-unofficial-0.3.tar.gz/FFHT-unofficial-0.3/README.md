# Fast Fast Hadamard Transform (unofficial)

The FFHT-unofficial library is a more recent python wrapper of the original FFHT library. The latter provides a heavily optimized C99 implementation of the Fast Hadamard Transform. For more informations, see https://github.com/FALCONN-LIB/FFHT.

The problem of the original FFHT library is that it relies on numpy C API which is no longer supported by recent numpy versions, it looks like no further updates are planned. One of the contributors did fix the issue in the fork https://github.com/dnbaker/FFHT by using pybind11 instead, and added a 2D support using parallélisation with OpenMP. However, there were still minor compilation problems, thus the library could not be installed from source.

The only objective of the FFHT-unofficial library is to distribute a slightly corrected version  of the latter fork. In a nutshell, the problem was solved only by adding the argument `extra_link_args=['-fopenmp']` in the initialization of the `Extension` class in `setup.py`.

# Installation

Installing the library requires a modern c++ compiler like `gcc`, as well as the python libraries `numpy` and `pybind11`. To install FFHT-unofficial from PYPI, run the lines below.

```
pip install --upgrade pip
pip install ffht-unofficial
```

# Usage

Within a python script, the FFHT-unofficial library is imported by `import ffht`. The library contains two functions, `ffht.fht_` and `ffht.fht`, respectively for the inplace and the out of place FHT. Note that those functions do not actually compute the Hadamard transform of a vector, but a scaled version. In order to obtain the isometric Hadamard transform, the results must by a factor `2**(-d/2)`, where `2**d` is the dimension of that data to transform. The code below provides an example of usage of the ffht functions for 1dim and 2dim numpy array. One can also see the `example.py` file.


```
import numpy as np
import ffht

# a 1dim array
x1 = np.random.normal(size=(2**20))

# a 2dim array
x2 = np.random.normal(size=(3, 2**20))

# out of place FHT
y1 = ffht.fht(x1)
y1 /= 2**(20/2) # rescale to obtain an isometry
y2 = ffht.fht(x2)
y2 /= 2**(20/2)

# in place FHT
ffht.fht_(x1)
x1 /= 2**(20/2)
ffht.fht_(x2)
x2 /= 2**(20/2)
```
