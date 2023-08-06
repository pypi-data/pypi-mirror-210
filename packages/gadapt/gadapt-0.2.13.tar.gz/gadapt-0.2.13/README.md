# GAdapt: Self-Adaptive Genetic Algorithm
**GAdapt** (https://gadapt.com) is an open-source Python library for Genetic Algorithm optimization. It implements innovative concepts for adaptive mutation of genes and chromosomes.

# What innovations does GAdapt bring?
**GAdapt** introduces self-adaptive determination of how many and which chromosomes and genes will be mutated. This determination is based on diversity of parents, diversity of cost and cross-diversity of genetic variables in the population. Less diversity increases the possibility of the mutation. Consequently, it increases the accuracy and the performance of the optimization. Default settings provide self-adaptive determination of mutation chromosomes and genes.


# Installation
To install [GAdapt] use pip, with the following command:
pip install gadapt

# Source Code
The source code is stored on GitHub, on the following address: https://github.com/bpzoran/gadapt

# Getting started
The following example optimizes variable values for a complex trigonometric function.
```python
from gadapt.ga import GA
import math

#trigonometric function definition
def trig_func(args):    
    return math.sqrt(abs(math.cos(args[0]))) + math.pow(math.cos(args[1]), 2) + math.sin(args[2]) + math.pow(args[3], 2) + math.sqrt(args[4]) + math.cos(args[5]) - (args[6]*math.sin(pow(args[6], 3)) + 1) + math.sin(args[0]) / (math.sqrt(args[0])/3 + (args[6]*math.sin(pow(args[6], 3)) + 1) ) / math.sqrt(args[4]) + math.cos(args[5])

#Instantiation of genetic algorithm for desired function
ga = GA(cost_function=trig_func)

#Adding variables (minimal value, maximal value and step)
ga.add(1.0, 4.0, 0.01)
ga.add(37.0, 40.0, 0.01)
ga.add(78.0, 88.0, 0.1)
ga.add(-5.0, 4.0, 0.1)
ga.add(1.0, 100.0, 1)
ga.add(1.0, 4.0, 0.01)
ga.add(-1, -0.01, 0.005)

#Execution of the genetic algorithm
results = ga.execute()

#Printing results
print(results)

"""
Possible output:
Min cost: -3.370583074871819
Number of iterations: 286
Parameter values:
0: 1.57
1: 39.27
2: 86.4
3: 0.0
4: 1.0
5: 3.14
"""
```
In this example, genetic algorithm searches for the combination of six parameters which bring the lowest value for the passed function. The only mandatory attribute to the genetic algorithm is cost_function, and other attributes in this example took default values. Parameters to be optimized are added by the "add" method. There are seven parameters to be optimized in this example.
# Parameter Settings
GAdapt genetic algorithm can receive parameters using constructor, properties, or combined.
Passing parameters through the class constructor:
```python
ga = GA(cost_function=trig_func,
    population_size=32,
    population_mutation="cost_diversity,parent_diversity",
    number_of_mutation_chromosomes=6,
    number_of_mutation_genes=2,
    exit_check="min_cost",
    max_attempt_no=20,
    logging=True,
    timeout=3600)
```
Passing parameters through the class properties:
```python
ga = GA()
ga.cost_function = trig_func
population_size=32
ga.population_mutation="cost_diversity,parent_diversity"
ga.number_of_mutation_chromosomes=6
ga.number_of_mutation_genes=2
ga.exit_check="min_cost"
ga.max_attempt_no=20
ga.logging=True
ga.timeout=3600
```
Passing parameters through the class constructor and properties:
```python
ga = GA(cost_function=trig_func, population_size=32)
ga.population_mutation="cost_diversity,parent_diversity"
ga.number_of_mutation_chromosomes=6
ga.number_of_mutation_genes=2
ga.exit_check="min_cost"
ga.max_attempt_no=20
ga.logging=True
ga.timeout=3600
```