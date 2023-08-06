from typing import List, Tuple
from gadapt.exit_check.base_exit_checker import BaseExitChecker
from gadapt.cost_finding.base_cost_finder import BaseCostFinder
from gadapt.crossover.base_crossover import BaseCrossover
from gadapt.ga_model.chromosome import Chromosome
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.gene import Gene
from gadapt.ga_model.genetic_variable import GeneticVariable
from gadapt.immigration.chromosome_immigration.base_chromosome_immigrator import BaseChromosomeImmigrator
from gadapt.immigration.population_immigration.base_population_immigrator import BasePopulationImmigrator
from gadapt.mutation.chromosome_mutation.base_chromosome_mutator import BaseChromosomeMutator
from gadapt.mutation.population_mutation.base_population_mutator import BasePopulationMutator
from gadapt.mutation.population_mutation.composed_population_mutator import ComposedPopulationMutator
from sklearn.preprocessing import MinMaxScaler
from gadapt.variable_update.base_variable_updater import BaseVariableUpdater
import gadapt.string_operation.ga_strings as ga_strings
from datetime import datetime
import gadapt.ga_model.definitions as definitions

class Population:

    def __init__(self, options: GAOptions,
                 chromosome_mutator: BaseChromosomeMutator,
                 population_mutator: BasePopulationMutator,
                 exit_checker: BaseExitChecker,
                 cost_finder: BaseCostFinder,
                 population_immigrator: BasePopulationImmigrator,
                 chromosome_immigrator: BaseChromosomeImmigrator,
                 selector,
                 crossover: BaseCrossover,
                 variable_updater: BaseVariableUpdater):
        if options.population_size < 4:
            raise Exception("Population size 4 must be higher than 3")        
        self.scaler = MinMaxScaler(feature_range=(1, 2))
        self.options = options
        self.chromosome_mutator = chromosome_mutator
        self.population_mutator = population_mutator
        self.exit_checker = exit_checker
        self.cost_finder = cost_finder
        self.population_immigrator = population_immigrator
        self.chromosome_immigrator = chromosome_immigrator
        self.selector = selector
        self.crossover = crossover
        self.variable_updater = variable_updater
        self.set_init_values()
        self.last_chromosome_id = 1
        self._population_generation = 0
        self.options = options
        self.chromosomes = []
        self.generate_initial_population()
        self.start_time = datetime.now()
        self.timeout_expired = False

    def __getitem__(self, index):
        return self.chromosomes[index]

    def __next__(self):
        return next(self.chromosomes)

    def __len__(self):
        return len(self.chromosomes)
    
    def __str__(self):
        return self.to_string()

    def get_sorted(self, key: None = None, reverse: bool = False):
        return sorted(self.chromosomes, key=key, reverse=reverse)

    def append(self, c: Chromosome):
        self.chromosomes.append(c)

    def generate_initial_population(self):
        for i in range(self.options.population_size):
            self.add_new_chromosome()

    def to_string(self):
        return ga_strings.population_to_string(self)

    def set_init_values(self):
        float_init_value = definitions.FLOAT_NAN
        self.avg_cost = float_init_value
        self.previous_avg_cost = float_init_value
        self.min_cost = float_init_value
        self.previous_min_cost = float_init_value
        self.first_cost = float_init_value

    @property
    def options(self) -> GAOptions:
        return self._options

    @options.setter
    def options(self, value: GAOptions):
        self._options = value

    @property
    def avg_cost(self) -> float:
        return self._avg_cost

    @avg_cost.setter
    def avg_cost(self, value: float):
        self._avg_cost = value

    @property
    def previous_avg_cost(self) -> float:
        return self._previous_avg_cost

    @previous_avg_cost.setter
    def previous_avg_cost(self, value: float):
        self._previous_avg_cost = value

    @property
    def min_cost(self):
        return self._min_cost

    @min_cost.setter
    def min_cost(self, value: float) -> float:
        self._min_cost = value

    @property
    def previous_min_cost(self):
        return self._previous_min_cost

    @previous_min_cost.setter
    def previous_min_cost(self, value: float) -> float:
        self._previous_min_cost = value

    @property
    def first_cost(self) -> float:
        return self._first_cost

    @first_cost.setter
    def first_cost(self, value: float):
        self._first_cost = value

    @property
    def best_individual(self) -> Chromosome:
        return self._best_individual

    @best_individual.setter
    def best_individual(self, value: Chromosome):
        self._best_individual = value

    @property
    def population_generation(self):
        return self._population_generation

    @population_generation.setter
    def population_generation(self, value):
        self._population_generation = value

    @property
    def chromosome_mutator(self) -> BaseChromosomeMutator:
        return self._chromosome_mutator

    @chromosome_mutator.setter
    def chromosome_mutator(self, value: BaseChromosomeMutator):
        self._chromosome_mutator = value

    @property
    def population_mutator(self) -> BasePopulationMutator:
        return self._population_mutator

    @population_mutator.setter
    def population_mutator(self, value: BasePopulationMutator):
        self._population_mutator = value

    def append_population_mutator(self, value: BasePopulationMutator):
        if self._population_mutator is None or not isinstance(self._population_mutator, ComposedPopulationMutator):
            self.population_mutator = ComposedPopulationMutator(self.options)
        self.population_mutator.append(value)

    @property
    def cost_finder(self) -> BaseCostFinder:
        return self._cost_finder

    @cost_finder.setter
    def cost_finder(self, value: BaseCostFinder):
        self._cost_finder = value

    @property
    def selector(self):
        return self._selector

    @selector.setter
    def selector(self, value):
        self._selector = value

    @property
    def population_immigrator(self) -> BasePopulationImmigrator:
        return self._population_immigrator

    @population_immigrator.setter
    def population_immigrator(self, value: BasePopulationImmigrator):
        self._population_immigrator = value

    @property
    def chromosome_immigrator(self) -> BasePopulationImmigrator:
        return self._chromosome_immigrator

    @chromosome_immigrator.setter
    def chromosome_immigrator(self, value: BasePopulationImmigrator):
        self._chromosome_immigrator = value

    @property
    def crossover(self) -> BaseCrossover:
        return self._crossover

    @crossover.setter
    def crossover(self, value: BaseCrossover):
        self._crossover = value

    @property
    def variable_updater(self) -> BaseVariableUpdater:
        return self._variable_updater

    @variable_updater.setter
    def variable_updater(self, value: BaseVariableUpdater):
        self._variable_updater = value

    @property
    def population_immigrator(self) -> BasePopulationImmigrator:
        return self._population_immigrator

    @population_immigrator.setter
    def population_immigrator(self, value: BasePopulationImmigrator):
        self._population_immigrator = value

    @property
    def cost_finder(self) -> BaseCostFinder:
        return self._cost_finder

    @cost_finder.setter
    def cost_finder(self, value: BaseCostFinder):
        self._cost_finder = value

    @property
    def exit_checker(self) -> BaseExitChecker:
        return self._exit_checker

    @exit_checker.setter
    def exit_checker(self, value: BaseExitChecker):
        self._exit_checker = value

    def exit(self) -> bool:
        self.population_generation += 1
        self.population_mutator.before_exit_check(self)
        return self.exit_checker.check(self)

    def immigrate(self):
        self.population_immigrator.immigrate(self)

    def select_mates(self) -> List[Tuple[Chromosome, Chromosome]]:
        return self.selector.select_mates(self)

    def mate(self):
        chromosome_pairs = self.select_mates()
        for chromosome1, chromosome2 in chromosome_pairs:
            offspring1, offspring2 = self.crossover.mate(chromosome1, chromosome2, self.population_generation)
            self.add_chromosomes((offspring1, offspring2))

    def mutate(self):
        self.population_mutator.mutate(self)

    def find_costs(self):
        self.previous_avg_cost = self.avg_cost
        self.previous_min_cost = self.min_cost
        self.cost_finder.find_costs_for_chromosome(self)

    def clear(self):
        self.chromosomes.clear()

    def clear_and_add_chromosomes(self, chromosomes: List[Chromosome]):
        self.chromosomes.clear()
        self.add_chromosomes(chromosomes)

    def add_chromosomes(self, chromosomes):
        for c in chromosomes:
            self.add_chromosome(c)

    def add_new_chromosome(self):
        chromosome = Chromosome(self.chromosome_mutator, self.chromosome_immigrator, self.population_generation)
        chromosome.chromosome_generation = 1
        self.add_chromosome(chromosome)

    def add_chromosome(self, chromosome):
        if len(self) >= self.options.population_size:
            return
        if chromosome.chromosome_id is None or chromosome.chromosome_id == -1:
            chromosome.chromosome_id = self.last_chromosome_id            
            self.last_chromosome_id += 1            
        if len(chromosome) == 0:
            for gv in self.options.genetic_variables:
                g = Gene(gv)
                chromosome.append(g)
        self.append(chromosome)

    def update_variables(self):
        self.variable_updater.update_variables(self)
    
