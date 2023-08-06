import sys
import numpy as np
from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup, find_packages

long_description = open('README.md').read()
extra_compile_args=[
    '-march=native', '-O3', '-Wall', '-Wextra', '-pedantic',
    '-Wshadow', '-Wpointer-arith', '-Wcast-qual','-Wstrict-prototypes', 
    '-Wmissing-prototypes', '-std=c++11', '-fopenmp']

module = Pybind11Extension(
    name='ffht',
    sources=["ffht/fht-pybind11.cpp", "ffht/fht.c", "ffht/fast_copy.c"],
    extra_compile_args=extra_compile_args,
    extra_link_args=['-fopenmp'],
    include_dirs=[np.get_include()] + ['ffht-unofficial/ffht']
    )

setup(name='FFHT-unofficial',
      version='0.3',
      author='Alexandre Pasco',
      url='https://github.com/alexandre-pasco/FFHT-unofficial',
      description='Fast implementation of the Fast Hadamard Transform (FHT)',
      long_description=long_description,
      long_description_content_type='text/markdown',
      license='MIT',
      keywords='fast Fourier Hadamard transform butterfly',
      packages=find_packages(),
      install_requires=['numpy ','pybind11'],
      include_package_data=True,
      ext_modules=[module])
