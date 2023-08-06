from gadapt.factory.ga_factory import GAFactory
from gadapt.ga_logging.logging_settings import init_logging
from gadapt.ga_model.ga_options import GAOptions
from gadapt.ga_model.ga_results import GAResults
from gadapt.ga_model.population import Population
import gadapt.ga_model.message_levels as message_levels

class GAExecutor:
    def __init__(self, ga_options: GAOptions, factory: GAFactory) -> None:
        if (not ga_options is None):
            self.ga_options = ga_options    
        self.factory = factory          


    def execute(self) -> GAResults:
        results = GAResults()
        try: 
            init_logging(self.ga_options.logging)                           
        except Exception as ex:
            results.messages.append((message_levels.WARNING, "Logging failed. Error message: {exc}".format(exc=str(ex))))
            self.ga_options.logging = False
        validator = self.factory.get_options_validator()
        validator.validate()
        if not validator.success:
            results.success = False
            results.messages = validator.validation_messages
            return results
        #try:
        chromosome_mutator = self.factory.get_chromosome_mutator()
        population_mutator = self.factory.get_population_mutator()
        exit_checker = self.factory.get_exit_checker()
        cost_finder = self.factory.get_cost_finder()
        population_immigrator = self.factory.get_population_immigrator()
        chromosome_immigrator = self.factory.get_chromosome_immigrator()
        selector = self.factory.get_parent_selector()
        gene_combination = self.factory.get_gene_combination()
        crossover = self.factory.get_crossover(
            gene_combination, chromosome_mutator, chromosome_immigrator)
        variable_updater = variable_updater=self.factory.get_variable_updater()
        population = Population(self.ga_options,
                                chromosome_mutator=chromosome_mutator,
                                population_mutator=population_mutator,
                                exit_checker=exit_checker,
                                cost_finder=cost_finder,
                                population_immigrator=population_immigrator,
                                chromosome_immigrator=chromosome_immigrator,
                                selector=selector,
                                crossover=crossover,
                                variable_updater=variable_updater)
        population.find_costs()
        while not population.exit():
            population.immigrate()
            population.mate()
            population.mutate()
            population.find_costs()            
        if population.timeout_expired:
            results.messages.append((message_levels.WARNING, "Timeout expired!"))
        best_individual = population.best_individual
        results.min_cost = population.min_cost
        results.number_of_iterations = population.population_generation
        for g in best_individual:
            results.result_values[g.genetic_variable.variable_id] = g.variable_value
        #except Exception as ex:
        #    results.success = False
        #    results.messages.append((message_levels.ERROR, str(ex)))
        return results
    
