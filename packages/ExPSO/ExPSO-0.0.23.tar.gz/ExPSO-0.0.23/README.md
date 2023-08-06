# Welcome to pspso's documentation!

# Exponential Particle Swarm Optimization for Global Optimization (ExPSO)

<p align="center" style=""> <img src="https://github.com/insafkraidia/ExPSO/blob/62b69fe475f026dcbab2d5339d8a05ce36b257a9/src/05.png"> </p>

The ExPSO package is a Python library that includes an algorithm designed to optimize machine and deep learning parameters/hyperparameters. The algorithm divides the swarm population into three subpopulations and utilizes a search strategy based on an exponential function, allowing particles to make large leaps in the search space. It also adapts the control of the velocity range of each particle to balance the exploration and exploitation search phases. The leaping strategy is integrated into the velocity equation, and a new linearly decreasing cognitive parameter is included in the proposed method, along with a dynamic inertia weight strategy. The algorithm is designed to make large jumps at the beginning of the search and then small jumps for further improvements in specific regions of the solution search space. To obtain further information, we recommend referring to the journal paper available at [Exponential Particle Swarm Optimization for Global Optimization (ExPSO)](https://ieeexplore.ieee.org/document/9837898/).

## Table of content

| Section                                | Description                                                            |
| -------------------------------------- | ---------------------------------------------------------------------- |
| [Installation](#installation)          | Installing the dependencies and ExPSO                                  |
| [Getting started](#requirements)       | Packages necessary to work with ExPSO                                  |
| [Available parameters](#parameters)    | Modifiable parameters in API with their possible values                |
| [Usage](#usage)                        | Usage example data                                                     |
| [Examples with public data](#examples) | Different examples for API                                             |
| [Results](#results)                    | Comparative study between ExPSO and PSO for CNN,LSTM, XLNET,MLP models |
| [References](#reference)               | References to cite                                                     |
| [License](#license)                    | Package license                                                        |

## Flowchart of the proposed ExPSO

<p align="center" style="max-width: 100%;height: 900px;width: 600px;"> <img src="https://github.com/insafkraidia/ExPSO/blob/62b69fe475f026dcbab2d5339d8a05ce36b257a9/src/01.png"> </p>

## Installation

ExPSO can be installed using [pip](https://pip.pypa.io/en/stable/), a tool
for installing Python packages. To do it, run the following command:

```
pip install ExPSO
```

**Current version:** 0.0.20

## Requirements

ExPSO requires Python >= 3.6.1 or later to run. For other Python
dependencies, please check the `pyproject.toml` file included
on this repository.

Note that you should have also the following packages installed in your system:

- numpy
- math
- tensorflow
- keras
- scikit-learn

## Parameters

| Parameter name                    | Parameter description                                                                                                                                                                                                                                                                                                                                                                                                                                         | Possible values |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| Objective function(ObjFunction)   | This is the function that the algorithm will attempt to optimize. It is the main goal of the algorithm and is determined by the user based on the problem they are trying to solve.                                                                                                                                                                                                                                                                           | List of floats  |
| The optimal cost (opt)            | Represents the target cost value for the optimization problem. It is used as a reference cost value to determine the termination criterion and assess the convergence of the optimization algorithm.                                                                                                                                                                                                                                                          | Float           |
| Threshold (thrshold)              | Determines the convergence criteria for the optimization algorithm. It sets the threshold for the improvement in the objective function value that indicates when to terminate the optimization process. The optimization iterations continue until the absolute value of the difference (gap) between the current global best cost and the opt value becomes smaller than or equal to the thrshold. Once this condition is met, the optimization terminates. | Float           |
| Dimensions (D)                    | This parameter refers to the number of variables or features that are present in the objective function. It is important to correctly specify the dimension in order to achieve accurate optimization.                                                                                                                                                                                                                                                        | Integer         |
| Number of particles (nPop)        | This refers to the number of agents or particles that will be used to search the solution space. Increasing the number of particles can help to find better solutions, but it also increases the computational cost.                                                                                                                                                                                                                                          | Integer         |
| Maximum iteration numbers (MaxIt) | This parameter specifies the maximum number of iterations that the algorithm will perform before terminating. The number of iterations can help to obtain a more accurate solution and reduce the risk of finding a suboptimal solution.                                                                                                                                                                                                                      | Integer         |
| Upper and lower bounds (ub,lb)    | These are the maximum and the lowest value in the search space                                                                                                                                                                                                                                                                                                                                                                                                | Float           |
| Number of runs (runs)             | This parameter refers to the number of times the algorithm will be run with the same parameters.                                                                                                                                                                                                                                                                                                                                                              | Integer         |

Note: It is important to set a reasonable value to ensure that the algorithm converges to a good solution without taking too long. To calculate the maximum number of iterations (MaxIt), we need to set first, the maximum number of function evaluations (Max_FES) based on the dimensionality (D) of the problem. If D is less than or equal to 6, then Max_FES is set to 50000. If D is equal to 10, then Max_FES is set to 100000. If D is greater than 10, then Max_FES is set to 1000000. Next, we calculate MaxIt by dividing Max_FES by the population size nPop and adding 1.

## Usage

Below is an example for using the ExPSO package.

1. Import the ExPSO class

```
from ExPSO import ExPSOClass
```

2. Define the objective function.

```
def ObjFunction(x):
    #instructions.....
    return ....
```

3. Create an instance of the ExPSO class from the ExPSO package with specified parameters, including the objective function, the optimal cost (opt), threshold (thrshold), dimensionality (D), population size (nPop), maximum iterations (MaxIt), lower bounds (lb), upper bounds (ub), and number of runs (runs).

```
expso = ExPSOClass.ExponentialParticleSwarmOptimizer(ObjFunction, opt=opt, thrshold=thrshold,
          D=D, nPop=nPop, MaxIt=MaxIt, lb=lb, ub=ub, runs=runs)
```

4. The ExPSO algorithm is then used to optimize the objective function

```
best_solution = expso.optimize()
```

<a name="item1"></a>

## Examples

### Experiment 1. ExPSO with rosenbrock function

<p align="center" style=""> <img src="https://github.com/insafkraidia/ExPSO/blob/62b69fe475f026dcbab2d5339d8a05ce36b257a9/src/10.png"> </p>

The following example demonstrates the optimization process of ExPSO using the rosenbrock function:

```
def ObjFunction(x):
    # rosenbrock function
    n = len(x)
    return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
# create an instance of the  ExPSOClass with the specified parameters
expso = ExPSOClass.ExponentialParticleSwarmOptimizer(ObjFunction, opt=0, thrshold=1e-08,
          D=1000, nPop=30, MaxIt=30, lb=-30, ub=30, runs=30)
# optimize the function using ExPSO and retrieve the best solution
best_solution = expso.optimize()
# print the best solution found
print(f"Best solution found: {best_solution}")
```

Outputs:

```
Best solution found:
{'GlobalBestCost': 0.0,
 'GlobalBestPosition': array([[-2.32808064e+00,  3.72638986e+00,  1.18030275e+01,
        -2.80199098e+01,  2.59328519e+01, -1.49057827e+01,
        -2.77256194e+00,  4.47054248e+00,  2.44699480e+01,
        -2.68899252e+01, -9.64479003e+00,  1.09886986e+01,
        -3.16572820e+00, -1.23867646e+01, -2.06098389e+01,
         1.86093654e+00,  1.71640639e+01,  1.89470347e+01,
         .................................................]]),
'Metrics': {'ExPSO': array([0., 0., 0., ..., 0., 0., 0.]),
 'MEAN': 0.0, 'WorstSol': 0.0, 'BestSol': 0.0, 'STD': 0.0, 'Avg_FES': 0.033296337402885685}}
```

- GlobalBestCost: It represents the optimal or near-optimal value achieved by the ExPSO algorithm.
- GlobalBestPosition: It represents the optimal or near-optimal solution obtained by the ExPSO algorithm in the search space.
- MEAN: It represents the average value of the best cost found across multiple optimization runs.
- WorstSol: It refers to the highest value of the best cost found during the optimization process. It helps evaluate the quality of the obtained solutions and identify the worst-performing solution.
- BestSol: It refers to the lowest value of the best cost found during the optimization process.
- STD (Standard Deviation): It refers to the standard deviation, which is often used to assess the diversity or convergence of the obtained solutions.
- Avg_FES (Average Function Evaluations): It represents the average number of function evaluations performed during the optimization process.

### Experiment 2. ExPSO with ackley function

<p align="center" style=""> <img src="https://github.com/insafkraidia/ExPSO/blob/62b69fe475f026dcbab2d5339d8a05ce36b257a9/src/08.png"> </p>

The following example demonstrates the optimization process of ExPSO using the ackley function:

```
def ObjFunction(x):
    # ackley function version 2.22
    z = -20*np.exp(-0.2*np.sqrt(np.sum(x**2, axis=1)/x.shape[1])) \
        - np.exp(np.sum(np.cos(2*np.pi*x), axis=1) /
                 x.shape[1]) + 20 + np.exp(1)
    return z
# create an instance of the  ExPSOClass with the specified parameters
expso = ExPSOClass.ExponentialParticleSwarmOptimizer(ObjFunction, opt=0, thrshold=1e-08,
          D=1000, nPop=30, MaxIt=30, lb=-5.12, ub=5.12, runs=30)
# optimize the function using ExPSO and retrieve the best solution
best_solution = expso.optimize()
# print the best solution found
print(f"Best solution found: {best_solution}")
```

### Experiment 3. ExPSO with CNN

The following example demonstrates the optimization process of ExPSO for the convolutional neural network (CNN):

```
def ObjFunction(particles):
    numberFilters = int(particles[0][0])  # FLOAT TO INT
    numberEpochs = int(particles[0][1])
    # CALL CNN FUNCTION cnn --> RETURN accuracy
    accuracy = cnn(x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test, batch_size=batch_size,
                    epochs=numberEpochs, filters=numberFilters, kernel_size=kernel_size, stride=stride)

    # APPLY LOST FUNCTION --> THE MAIN OBJECTIVE IS TO MINIMIZE LOSS --> MAXIMIZE ACCURACY AND AT SAME TIME MINIMIZE THE NUMBER OF EPOCHS
    # AND FILTERS, TO REDUCE TIME AND COMPUTACIONAL POWER
    loss = 1.5 * ((1.0 - (1.0/numberFilters)) +
                    (1.0 - (1.0/numberEpochs))) + 2.0 * (1.0 - accuracy)
    return loss  # NEED TO RETURN THIS PYSWARMS NEED THIS

def main():
    pt = -4.189829e+05
    thrshold = 1
    nPop = 30
    runs = 20
    lb = 1
    ub = 500
    D = 2
    Max_FES = 50000
    MaxIt = int(Max_FES/nPop) + 1
    # create an instance of the ExPSOClass class with the specified parameters
    pso = ExPSOClass.ExponentialParticleSwarmOptimizer(ObjFunction, opt=opt, thrshold=thrshold,
                                                        D=D, nPop=nPop, MaxIt=MaxIt, lb=lb, ub=ub, runs=runs)
    # optimize the function using ExPSO and retrieve the best solution
    cost, pos, _ = pso.optimize()
```

Note: The file "tests/ExPSOWithCNN.py" contains the entire code for the implementation of the ExPSO algorithm with a Convolutional Neural Network (CNN).

### Experiment 4. ExPSO with LSTM

The following example demonstrates the optimization process of ExPSO for the Long short-term memory (LSTM):

```
def ObjFunction(particle):
    neurons = int(particle[0][0])
    epochs = int(particle[0][1])
    # CALL LSTM_MODEL function
    accuracy = lstm(x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test,
                    neurons=neurons, epochs=epochs)
    # APPLY COST FUNCTION --> THIS FUNCTION IS EQUALS TO CNN COST FUNCTION
    loss = 1.5 * ((1.0 - (1.0/neurons)) + (1.0 - (1.0/epochs))
                    ) + 2.0 * (1.0 - accuracy)
    return loss


def main():
    opt = -4.189829e+05
    thrshold = 1
    nPop = 30
    runs = 20
    lb = 1
    ub = 200
    D = 2
    Max_FES = 50000
    MaxIt = int(Max_FES/nPop) + 1
    # create an instance of the ExPSOClass class with the specified parameters
    pso = ExPSOClass.ExponentialParticleSwarmOptimizer(ObjFunction, opt=opt, thrshold=thrshold,
                                                       D=D, nPop=nPop, MaxIt=MaxIt, lb=lb, ub=ub, runs=runs)
    # optimize the function using ExPSO and retrieve the best solution
    cost, pos, _ = pso.optimize()
```

Note: The file "tests/ExPSOWithLSTM.py" contains the entire code for the implementation of the ExPSO algorithm with Long short-term memory (LSTM).

### Experiment 5. ExPSO with XLNET

The following example demonstrates the optimization process of ExPSO for XLNET:

```
def ObjFunction(particles):
    oss = alexNet(particleDimensions=particles, x_train=x_train, x_test=x_test,
                       y_train=y_train, y_test=y_test)
    return loss

def main():
    opt = -4.189829e+05
    thrshold = 1
    nPop = 30
    runs = 10
    lb = 32
    ub = 160
    D = 5*30
    Max_FES = 1000000
    MaxIt = int(Max_FES/nPop) + 1
    # create an instance of the ExPSOClass class with the specified parameters
    pso = ExPSOClass.ExponentialParticleSwarmOptimizer(ObjFunction, opt=opt, thrshold=thrshold,
                                                       D=D, nPop=nPop, MaxIt=MaxIt, lb=lb, ub=ub, runs=runs)
    # optimize the function using ExPSO and retrieve the best solution
    cost, pos, _ = pso.optimize()
```

Note: The file "tests/ExPSOWithXlNET.py" contains the entire code for the implementation of the ExPSO algorithm with XLNET.

### Experiment 6. ExPSO with MLP

The following example demonstrates the optimization process of ExPSO for the multilayer perceptron (MLP):

```
def ObjFunction(particles):
    allLosses = mlp(particleDimensions=particles, x_train=x_train, x_test=x_test,
                        y_train=y_train, y_test=y_test)

    return allLosses

def main():
    opt = -4.189829e+05
    thrshold = 1
    nPop = 30
    runs = 10
    lb = 1
    ub = 500
    D = 2
    Max_FES = 50000
    MaxIt = int(Max_FES/nPop) + 1
    # create an instance of the ExPSOClass class with the specified parameters
    pso = ExPSOClass.ExponentialParticleSwarmOptimizer(ObjFunction, opt=opt, thrshold=thrshold,
                                                       D=D, nPop=nPop, MaxIt=MaxIt, lb=lb, ub=ub, runs=runs)
    # optimize the function using ExPSO and retrieve the best solution
    cost, pos, _ = pso.optimize()
```

Note: The file "tests/ExPSOWithMLP.py" contains the entire code for the implementation of the ExPSO algorithm with multilayer perceptron (MLP).

## Results

In [Exponential Particle Swarm Optimization for Global Optimization (ExPSO)](https://ieeexplore.ieee.org/document/9837898/), several analysis methods and a comparative study are presented to demonstrate the performance of this technique. In below figure, we compared our library with:

- Fuzzy Self-Tuning PSO (FST-PSO) https://pypi.org/project/fst-pso/.
- Pyswarms: a reference librarythat used pure PSO (Particle Swarm Optimization). https://github.com/ljvmiranda921/pyswarms .
- Quantum particle swarm optimization (QPSO) https://pypi.org/project/qpso/.
- FastPSO :Fast parallel Particle Swarm Optimization package (FastPSO) https://pypi.org/project/fastPSO/.

The findings demonstrate notable advancements and efficient optimization achieved through ExPSO for various models such as CNN, LSTM, XLNET, and MLP.

<p align="center" style=""> <img src="https://github.com/insafkraidia/ExPSO/blob/62b69fe475f026dcbab2d5339d8a05ce36b257a9/src/88.png"> </p>

## Reference

If you use `ExPSO` in your research papers, please refer to it using following reference:

```
[Exponential Particle Swarm Optimization for Global Optimization (ExPSO)](https://ieeexplore.ieee.org/document/9837898/)

```

## License

`ExPSO` is released under the terms of the GNU General Public License (GPL).
