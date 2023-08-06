# Python-based Atomistic Spin Dynamics simulator (pyasd)

This is a python package for spin dynamics simulations

Copyright Shunhong Zhang 2023

zhangshunhong.pku@gmail.com


## Code distributions

* core: core scripts for spin dynamics simulations
* utility: scripts for post-processing, applied to the current code and Spirit
* data_base: some exchange parameters for typical magnetic materials, udner construction
* mpi: some scripts for parallelization implementing mpi4py
* examples: some examples to do fast test on the code
* tests_basic: some testing cases

## Installation
* Fast installation via pypi
pip install pyasd


* Install manually from tarball 
1. Download the zip or tarball (tar.gz) of the package
2. unzip the package
3. Run one of the two following command
   python setup.py install --home=.
   python setup.py install --user

* To check whether you have successfully install the package, go to the python interactive shell
 
import asd.core
import asd.data_base
import asd.utility
import asd.mpi

If everything runs smoothly, the installation should be done. 
Contact the author if you come across any problem.


## Clean installation
./clean

This operation removes "build" and "dists" directories generated upon compilation
and results in the examples/tests_basic directory, including dat and ovf files, and figures in png
