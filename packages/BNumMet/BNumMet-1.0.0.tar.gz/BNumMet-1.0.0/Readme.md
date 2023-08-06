# BNumMet
***
- Title: BNumMet
- Author: Fernando Bellido Pazos ([fbellidopazos@gmail.com](fbellidopazos@gmail.com))
- Date: 2022
- Version: 1.0.0
- License: GNU Affero General Public License v3.0 (AGPL-3.0)
- Description: A Scholar implementation of Numerical Methods in Python enhanced with interactive widgets
- Tags: Numerical methods, Open-source, Python, Jupyter, Software development, Linear systems, Interpolation, Nonlinear, Least squares, Random number generators
- URL: [Python_BNumMet](https://github.com/fbpazos/Trabajo-Fin-Master/tree/main/Python_BNumMet)

## Table of Contents
---
<!-- TOC start -->
- [Introduction](#introduction)
- [Installation](#installation)
  * [PyPi Package Manager](#pypi-package-manager)
  * [Manual Installation](#manual-installation)
- [Continue Development](#continue-development)
  * [Run Tests](#run-tests)
- [BNumMet - Structure](#bnummet---structure)
- [Usage & Examples](#usage--examples)
  * [Linear Systems](#linear-systems)
  * [Interpolation](#interpolation)
  * [Non-Linear](#non-linear)
  * [Randomness](#randomness)
  * [Visualizers](#visualizers)
    + [Linear Systems](#linear-systems-1)
    + [Interpolation](#interpolation-1)
    + [Non-Linear](#non-linear-1)
    + [Least Squares](#least-squares)
    + [Randomness](#randomness-1)
- [SonarQube](#sonarqube)
  * [Start the SonarQube server (Docker Version)](#start-the-sonarqube-server-docker-version)
  * [Run the analysis](#run-the-analysis)
<!-- TOC end -->
## Introduction
---
BNumMet (`/bi: num mεt/`) is short for Basic Numerical Methods. It is a self-contained library that provides students with a scholarly implementation of numerical methods alongside a visual interface that captures the essence of the methods explained.

The intention and purpose of this library are to provide students with an introduction to both Python and numerical methods that will serve them in their future in the academic and enterprise world. It uses NumPy, as students will find it in their everyday life while using numerical methods in Python.

## Installation
---
There are two main ways to install the package, using the pypi package installer or manual installation

### PyPi Package Manager
Since the package is publicly available in the PyPi webpage ([https://pypi.org/project/BNumMet/](https://pypi.org/project/BNumMet/)), we can use the 'pip' command.

Assuming a correct installation of Python and/or pip, the following command will install all dependencies and the package:
  
  ```bash
  pip install BNumMet
  ```
### Manual Installation

Alternatively, you can download the repository and install the package manually. To do so, you can use the following commands:
1. Clone the repository: [https://github.com/fbpazos/Trabajo-Fin-Master](https://github.com/fbpazos/Trabajo-Fin-Master), there are two ways, using git and a manual cloning
    1. Using git: `git clone https://github.com/fbpazos/Trabajo-Fin-Master`
    2. Manual cloning: Click on [https://github.com/fbpazos/Trabajo-Fin-Master/archive/refs/heads/main.zip](https://github.com/fbpazos/Trabajo-Fin-Master/archive/refs/heads/main.zip), this will download a zip file with the latest version. Extracting this will provide the cloning.
2. Install using Python: Once cloned, `cd` into the folder named as `Python_BNumMet`, and write in a terminal one of these two options:
    1. Using pure Python: `python setup.py install`
    2. Using pip locally: `pip install .`

## Continue Development
---
If anyone desires to continue the development, respecting the license provided, we recommend the use of virtual environments to externalize the current installation of other libraries when developing BNumMet.

1. Clone the repository: [https://github.com/fbpazos/Trabajo-Fin-Master](https://github.com/fbpazos/Trabajo-Fin-Master), there are two ways, using git and a manual cloning
    1. Using git: `git clone https://github.com/fbpazos/Trabajo-Fin-Master`
    2. Manual cloning: Click on [https://github.com/fbpazos/Trabajo-Fin-Master/archive/refs/heads/main.zip](https://github.com/fbpazos/Trabajo-Fin-Master/archive/refs/heads/main.zip), this will download a zip file with the latest version. Extracting this will provide the cloning.

2. (Optional) Create the virtual environment and activate it: Once cloned, 'cd' into the folder named as 'Python\_BNumMet', proceed with the following commands
    1. Using CMD: `python3 -m venv venv && source venv/bin/activate`
    2. Using Bash: `python -m venv venv && venv\Scripts\activate`

3. Install the package in editable mode: In contrast to normally installing the library as we aforementioned, editable mode allows us to make changes to the library and those changes will automatically be updated into the python installation, to properly install it using this mode: `pip install -e .` , the '-e' indicates editable, it could also be written as `--editable`

4. (Optional, highly recommended) Install development dependencies: To properly test the library, we recommend installing the development dependencies, to do so, use the following command: `pip install -r requirements_dev.txt`

When continuing development, make sure to add tests to new/old functions as well as passing a SonarQube's analysis, therefore we assure good-quality standards to the students.

### Run Tests
In order to properly run the tests, we recommend using the following commands:
```bash
pytest # Run tests
```
Or, alternatively, you can use the \_\_init\_\_.py file to run the tests.

```bash
python tests/__init__.py # Run tests

# It will generate a coverage report in the Tests/coverage folder in different formats (html, xml, lcov). 
# It will also format the code using the Black Library (I Might've forgottent to do so :) )
```
## BNumMet Library Structure

```
BNumMet
	* LinearSystems
		- lu( matrix ) --> P,L,U matrices as np.array
		- permute( matrix, row_1, row_2) --> Permuted Matrix as np.array
		- forward_substitution( matrix_L, matrix_b ) --> Solution to Lx=b as np.array
		- backward_substitution( matrix_U, matrix_b ) --> Solution to Ux=b as np.array
		- lu_solve ( matrix_A, matrix_b ) --> Solution to Ax=b as np.array using LU Decomposition
		- qr_factorization ( matrix_A ) --> Q,R Matrices as np.array
		- qr_solve( matrix_A, matrix_b ) --> Solution to Ax=b as np.array using QR decomposition
 		- interactive_lu( matrix_p, matrix_l, matrix_u, col, row, pivot_row) --> An iteration of LU Decomposition
	* Interpolation
		- polinomial(interpolation_x, interpolation_y, mesh) --> Polinomial-Interpolated values over mesh
		- piecewise_linear(interpolation_x, interpolation_y, mesh) --> Piecewise Linear-Interpolated values over mesh
		- pchip(interpolation_x, interpolation_y, mesh) --> Piecewise Cubic Hermite-Interpolated values over mesh
		- splines(interpolation_x, interpolation_y, mesh) --> Piecewise Cubix-Interpolated values over mesh
	* NonLinear
		- bisect( function, interval:tuple, stop_iters:int, iters:bool, *args) --> x-value of where the zero is at and as optional the number of iterations taken
		- secant( function, interval:tuple, stop_iters:int, iters:bool, *args) --> x-value of where the zero is at and as optional the number of iterations taken
		- newton( function, derivative, interval:tuple, stop_iters:int, iters:bool, *args) --> x-value of where the zero is at and as optional the number of iterations taken
		- IQI( function, values_of_x:tuple, stop_iters:int, iters:bool, *args) --> x-value of where the zero is at and as optional the number of iterations taken
		- zBrentDekker( function, interval:tuple, tol, stop_iters:int, iters:bool, *args) --> x-value of where the zero is at and as optional the number of iterations taken	
	* Random
		- clear_lehmers_vars() --> Cleans the initiated values of the Lehmers random number generator
		- lehmers_init(a, c, m, x) --> Initializes Lehmers R.N.G. with values given
		- lehmers_rand(a, c, m, x) --> Initializes and produces a random number every time it is called
		- clear_marsaglia_vars() --> Cleans the initiated values of the Marsaglia's random number generator
		- marsaglia_init(base, lag_r, lag_s, carry, seed_tuple) --> Initializes Marsaglia's R.N.G. with values given
		- marsaglia_rand(base, lag_r, lag_s, carry, seed_tuple) --> Initializes and produces a random number every time it is called
		- clear_mt_vars() --> Cleans the initiated values of the Mersenne Twister random number generator
		- sgenrand(seed:int) --> Initializes and produces a random number every time it is called
	* Visualizers
		- LUVisualizer
			- LUVisualizer:Class 
		- InterpolationVisualizer
			- InterpolVisualizer:Class 
		- NonLinearVisualizer
			- NonLinearVisualizer:Class 
		- LeastSquaresVisualizer
			- LSPVisualizer:Class 
		- RandomVisualizer
			- RandomVisualizer:Class 
```

## BNumMet - Structure
----
```bash
.
├── Demos # Contains the Jupyter Notebooks with the demos
│   ├── Interpolation.ipynb
│   ├── LinearSystems.ipynb
│   ├── NonLinear.ipynb
│   ├── Packages Show.ipynb
│   ├── Randomness.ipynb
│   └── Timings # Contains the Jupyter Notebooks with the timings results
│       ├── Interpolation Timings.py
│       ├── Interpolation_Timings_Analysis.ipynb
│       ├── LU_Timings_Analysis.ipynb
│       ├── Linear Systems Timings.py
│       ├── NonLinear Timings.py
│       ├── NonLinear_Iterations.ipynb
│       └── Results
├── LICENSE
├── MANIFEST.in
├── Readme.md
├── Utilities # Contains the utilities to run the tests and the SonarQube analysis
│   ├── ReportGenerator.jar
│   ├── SonarScanner.bat
│   ├── SonarScanner.sh
│   ├── ngrok.exe
│   └── sonarqubeRemote.bat
├── VERSION
├── pyproject.toml
├── requirements.txt
├── requirements_dev.txt
├── setup.cfg
├── setup.py
├── src
│   └── BNumMet # Contains the source code of the package
│       ├── Interpolation.py
│       ├── LinearSystems.py
│       ├── NonLinear.py
│       ├── Random.py
│       ├── Visualizers # Contains the visualizers of the package
│       │   ├── InterpolationVisualizer.py
│       │   ├── LUVisualizer.py
│       │   ├── LeastSquaresVisualizer.py
│       │   ├── NonLinearVisualizer.py
│       │   └── RandomVisualizer.py
│       ├── __init__.py
│       └── module.py
├── tests # Contains the tests of the package
│   ├── Reports # Contains the reports generated by the tests
│   │   └── testsReport.xml
│   ├── __init__.py
│   ├── test_General.py
│   ├── test_Interpolation.py
│   ├── test_LeastSquares.py
│   ├── test_LinealSystems.py
│   ├── test_NonLinear.py
│   ├── test_Random.py
│   └── test_module.py
└── tox.ini
```


## Usage & Examples
---
### Linear Systems

```python
from BNumMet.LinearSystems import lu
A = np.array([[10, -7, 0], [-3, 2, 6], [5, -1, 5]])
P, L, U = lu(A)
display(P, L, U)

>> P = array([ [1., 0., 0.],
               [0., 0., 1.],
               [0., 1., 0.]])
>> L = array([ [ 1.  ,  0.  ,  0.  ],
               [ 0.5 ,  1.  ,  0.  ],
               [-0.3 , -0.04,  1.  ]])
>> U = array([ [10. , -7. ,  0. ],
               [ 0. ,  2.5,  5. ],
               [ 0. ,  0. ,  6.2]])
```

### Interpolation

```python
from BNumMet.Interpolation import pchip
x = list(np.arange(1, 7, 1))
y = [16, 18, 21, 17, 15, 12]
u = np.arange(0.8, 6.2, 0.05)
v = pchip(x, y, u)
# Plotting using Matplotlib
plt.plot(u, v, "b-", label="Interpolated")
plt.plot(x, y, "ro", label="Original Points")
plt.legend()
plt.show()
```

![Interpolation](https://dub07pap002files.storage.live.com/y4m52-hsxWxH8zjFakW7db0zDr1AGGI4j3VL3PTT_g5KO0AiotCnUBwwO5I9sSXIToLvJnfWtCBaOyZLukE_JBryO-JNNkodo2W0xjneL0cDoDy3CZaoFC-d8N0XbkOAWYjZgcu3M1K-j74BgEXUL5-oV6S_yLayyCtUl30xP6BPlC6bio1ZqPtqs2mARBgEP7e?encodeFailures=1&width=543&height=413)

### Non-Linear

```python
from BNumMet.NonLinear import zBrentDekker
fun = lambda x: x**2 - 2
interval = [1, 2]
sol, nIter = zBrentDekker(fun, interval, iters = True)
print("Brent-Dekker method: x = %f, nIter = %d" % (sol, nIter))

>> Brent-Dekker method: x = 1.414214, nIter = 7
```

### Randomness

```python
from BNumMet.Random import marsaglia_rand, clear_marsaglia_vars
clear_marsaglia_vars()
fail = [
    (
        marsaglia_rand(base=41, lag_r=2, lag_s=1, carry=0, seed_tuple=(0, 1)),
        marsaglia_rand(base=41, lag_r=2, lag_s=1, carry=0, seed_tuple=(0, 1)),
    )
    for i in range(100000)
]
plt.scatter(*zip(*fail), s=1, c="black")
plt.show()
```
![Randomness](https://dub07pap002files.storage.live.com/y4mzE0abSi6MSC6wlcNO6cc7HkixFGCybt2guF2nrsuJevEeYJ01VOcaZ244FjFpN27PlSrAUucq_62p8wlyPdlkW1hEGJTD2ngxsI5DX8KtFOGtFqfHSyijZiYvKO4D2QoeURctNgIbgg75bzDNkiYWIjcJhXbwdipgxoLEuQItQBXjEX3vGcH134768ZZXfF_?encodeFailures=1&width=547&height=413)

### Visualizers
#### Linear Systems
```python
from BNumMet.Visualizers.LUVisualizer import LUVisualizer
luVisualizer = LUVisualizer()
display(luVisualizer.run())
```
![LUVisualizer](https://dub07pap002files.storage.live.com/y4m1q7uSd3dG2sMftf0YKDwNnz7aLGBnXeclboMbvU5un83LIpfX4Pw-8MJCHRzYcwLocDkZ1BeeAEx3qaowz7GUROV2rDzAYvmCcDEMw-X9P2HzXU9U3BzSMAQISEyUxxvVp3aNi46blEf1c1Liw_cADasxsqjOaZwwrrwTP7x7awPTudf0z4GwEmO2RH_akoB?encodeFailures=1&width=1080&height=404)

#### Interpolation
```python
from BNumMet.Visualizers.InterpolationVisualizer import InterpolVisualizer
interpolVisualizer = InterpolVisualizer()
display(interpolVisualizer.run())
```
![interpolVisualizer](https://dub07pap002files.storage.live.com/y4mIg9iw5xzbHxOkHF5tfZGqdjS2yob1Zzd6LXkedOdQE8RBt54lqqfLUX8XB2113dOYLKqzjph5GDzoYvp-Qf7uaqL8NQ_GH0CBYfTQNT1FIqB6Yn-KO4dT78rau9Ka1FfR5zsbToR24NJnkJX5jy-xymWato5cUJ4aDJqAz_ENPJA2n1nNkCaFQ7WX58tmqzz?encodeFailures=1&width=952&height=551)


#### Non-Linear
```python
from BNumMet.Visualizers.NonLinearVisualizer import NonLinearVisualizer
zerosVisualizer = NonLinearVisualizer()
zerosVisualizer.run()
```
![zerosVisualizer](https://dub07pap002files.storage.live.com/y4m1UJWkc5j50NF4KZd1w9VENgIqMT-GMjhE-qhKLIdF3K-ymR4Rttav5ZwUjSaCDFzuz0mYyDPS-5MBo89JEyTOO-P5PdwXoJN4rCO1vlrn_MxwTHLsscwHGFITW_0KwLW1cWi0u5EAtXphyBQf_tCH-OT5aqPQT8TS6urP1bgeHDrmAm6twsn0E2AqWKhbMpX?encodeFailures=1&width=864&height=711)


#### Least Squares
```python
from BNumMet.Visualizers.LeastSquaresVisualizer import LSPVisualizer
xData = np.array([0, 1, 2, 3, 4, 5])
yData = np.array([4.5, 2.4, 1.5, 1, 1.5, 2.4])
lspVisualizer = LSPVisualizer(xData, yData)
lspVisualizer.run()
```
![lspVisualizer](https://dub07pap002files.storage.live.com/y4mJQgX2hkcE5PU_vExDNiJb3-xPapyxDQqf7yZbw1uJ3kkxv5gxwsmYb13hUqf_IYyxdp9cZJHUP4UPYCuXzXs_hh27XFdwF5e6DsQSr0JGfKQhxivPBD6B_90wSpatlXWFG47NPzC5SxsDcM8Mj0u50hQUCGdXsbpGHHY5eDnB-CL_E2I1F0F0CkNPnAna5XW?encodeFailures=1&width=794&height=465)

#### Randomness
```python
from BNumMet.Visualizers.RandomVisualizer import RandomVisualizer
randomVisualizer = RandomVisualizer()
randomVisualizer.run()
```
![randomVisualizer](https://dub07pap002files.storage.live.com/y4mE3vUbK5Q6OnxGwiw3aQCfp8TrjYyo9mNdVMs1qjLWA3hNpGcLtisRHQZRXQEOEmdU3b3LLH4OLDgfgUFT2GrO4ktOIa6nyKB10ICQR_WIEyS-LPyM1NDXdEmKhe8uafPjJdJy8-fJI9y9t-tiuOaDZFGedaHBDfFZCvTZbYKvHgDmRrqycXAp7vx1lesvPLv?encodeFailures=1&width=722&height=758)









## SonarQube
---
In order to run the SonarQube analysis, you can use the following command:

### Start the SonarQube server (Docker Version)

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube
```
Since its running locally, you can access the server at http://localhost:9000, and the default credentials are admin/admin. 
Additionally, for simplicity with login go to Administration -> Security -> Disable "Force User Authentication". (This is not recommended for production environments)


### Run the analysis

Remeber the credentials here are admin/1234 but you can change them in the sonarqube server.

Linux 
```bash
docker run --rm -ti -v "$(pwd)":/usr/src \
--link sonarqube newtmitch/sonar-scanner sonar-scanner \
-Dsonar.login="admin" \
-Dsonar.password="1234" \
-Dsonar.projectName="BNumMet" \
-Dsonar.projectKey="BNumMet" \
-Dsonar.sources="src/BNumMet/" \
-Dsonar.python.version=3 \
-Dsonar.python.xunit.reportPath="tests/Reports/testsReport.xml" \
-Dsonar.python.coverage.reportPaths="tests/Reports/Coverage/xml/coverage.xml" \
-Dsonar.scm.disabled=true \
-Dsonar.tests="tests" \
-Dsonar.test.inclusions="tests/**" \
-Dsonar.test.exclusions="tests/Reports/Coverage/**"

```

Windows - just replace "$(pwd)" with "%cd%" 

```cmd
docker run --rm -ti -v "%cd%":"/usr/src" \
--link sonarqube newtmitch/sonar-scanner sonar-scanner \
-Dsonar.login="admin" \
-Dsonar.password="1234" \
-Dsonar.projectName="BNumMet" \
-Dsonar.projectKey="BNumMet" \
-Dsonar.sources="src/BNumMet/" \
-Dsonar.python.version=3 \
-Dsonar.python.xunit.reportPath="tests/Reports/testsReport.xml" \
-Dsonar.python.coverage.reportPaths="tests/Reports/Coverage/xml/coverage.xml" \
-Dsonar.scm.disabled=true \
-Dsonar.tests="tests" \
-Dsonar.test.inclusions="tests/**" \
-Dsonar.test.exclusions="tests/Reports/Coverage/**"
```




 

