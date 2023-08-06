from gadapt.validation.base_options_validator import BaseOptionsValidator
import gadapt.ga_model.definitions as definitions
import gadapt.ga_model.definitions as definitions
class CommonOptionsValidator(BaseOptionsValidator):

    def __init__(self, options) -> None:
        super().__init__(options)
        self._validation_messages = []        

    def validate(self):        
        self.success &= self.check_nones_types_and_values()
        self.success &= self.check_genetic_variables()
        self.success &= self.check_cost_function()
        
    
    def check_genetic_variables(self) -> bool:
        if self.options._genetic_variables is None:
            return False
        rslt = True
        for v in self.options._genetic_variables:
            if v.min_value is None or v.max_value is None or v.step is None:
                self.add_message("Min value, max value and step must not be None! (Variable {var_no})".format(var_no = v.variable_id))
                rslt &= False
            elif not (isinstance(v.min_value, float) or isinstance(v.min_value, int)) or not (isinstance (v.max_value, float) or isinstance (v.max_value, int)) or not (isinstance(v.step, float) or isinstance(v.step, int)) :
                self.add_message("Min value, max value and step must be float or int values! (Variable {var_no})".format(var_no = v.variable_id))
                rslt &= False
            elif v.min_value > v.max_value:
                self.add_message("Min value must be less or equal than max value! (Variable {var_no})".format(var_no = v.variable_id))
                rslt &= False
            elif v.step <= 0.0:
                self.add_message("Step must be positive float value! (Variable {var_no})".format(var_no = v.variable_id))
                rslt &= False
            elif v.min_value + v.step > v.max_value:
                self.add_message("Invalid step value! (Variable {var_no})".format(var_no = v.variable_id))
                rslt &= False
            if v.decimal_places < 0:
                self.add_message("Invalid number of decimal places! (Variable {var_no})".format(var_no = v.variable_id))
                rslt &= False
        return rslt
    
    def check_cost_function(self):
        if self.options.cost_function is None:
            self.add_message("Cost Function must not be None!")
            return False
        elif not callable(self.options.cost_function):
            self.add_message("Cost Function must be callable!")
            return False
        kwargsmin = {}
        kwargsmax = {}
        for v in self.options._genetic_variables:
            kwargsmin[v.variable_id] = v.min_value
            kwargsmax[v.variable_id] = v.max_value
        try:
            func_result_min = self.options.cost_function(kwargsmin)
            func_result_max = self.options.cost_function(kwargsmin)
            if not isinstance(func_result_min, float) or not isinstance(func_result_max, float):
                self.add_message("The function must return float value!")
                return False
        except KeyError:
            self.add_message("Inadequate number of parameters for the passed function!")
            return False
        except Exception as ex:
            self.add_message("An exception raised on the function call: {exc}".format(exc=str(ex)))
            return False
        return True
    
    def check_nones_types_and_values(self) -> bool:
        rslt = True
        population_size = 0
        if self.options.population_size is None:
            self.add_message("Population size must not be None!")
            rslt &= False
        elif not isinstance(self.options.population_size, int):
            self.add_message("Population size type must be int!")
            rslt &= False
        elif self.options.population_size < 4 or self.options.population_size > 65536:
            self.add_message("Population size must be an int between 4 and 65536!")
            rslt &= False
        else:
            population_size = self.options.population_size
        immigration_number = 0
        if self.options.immigration_number is None:
            self.add_message("Immigration Number must not be None!")
            rslt &= False
        elif not isinstance(self.options.immigration_number, int):
            self.add_message("Immigration Number must be type int!")
            rslt &= False
        elif population_size > 0 and self.options.immigration_number > population_size - 1:
            self.add_message("Immigration Number must not be type same or greater than population size!")
            rslt &= False        
        elif self.options.immigration_number < 0:
            self.add_message("Immigration Number must ne eqals or greather than 0!")
            rslt &= False
        else:
            immigration_number = self.options.immigration_number
        if self.options.number_of_mutation_chromosomes is None:
            self.add_message("Number of Mutation Chromosomes must not be None!")
            rslt &= False
        elif not isinstance(self.options.number_of_mutation_chromosomes, int):
            self.add_message("Number of Mutation Chromosomes must be type int!")
            rslt &= False
        else:
            if (self.options.number_of_mutation_chromosomes < 0) or (population_size > 0 and self.options.number_of_mutation_chromosomes > (population_size // 2) - immigration_number):
                self.add_message("Invalid number of mutation chromosomes: {0}".format(str(self.options.number_of_mutation_chromosomes)))
                rslt &= False
        if self.options._genetic_variables is None:
            self.add_message("Genetic variables must not be None!")
            rslt &= False
        number_of_genetic_variables = len(self.options._genetic_variables) 
        if number_of_genetic_variables < 1:
            self.add_message("At least one genetic variable must be added!")
            rslt &= False
        if self.options.number_of_mutation_genes is None:
            self.add_message("Number Of Mutation Variables must not be None!")
            rslt &= False
        elif not isinstance(self.options.number_of_mutation_genes, int):
            self.add_message("Number Of Mutation Variables must be type int!")
            rslt &= False
        elif (self.options.number_of_mutation_genes < 0) or (number_of_genetic_variables > 0 and self.options.number_of_mutation_genes > number_of_genetic_variables):
            self.add_message("Invalid number of mutation variables: {0}".format(str(self.options.number_of_mutation_genes)))
            rslt &= False
        if self.options.max_attempt_no is None:
            self.add_message("Max Attempt No must not be None!")
            rslt &= False
        elif not isinstance(self.options.max_attempt_no, int):
            self.add_message("Max Attempt No must be type int!")
            rslt &= False
        elif self.options.max_attempt_no < 1 or self.options.max_attempt_no > 65536:
            self.add_message("Max Attempt No must be type an int between 1 and 65536!")
            rslt &= False                                                           
        if self.options.chromosome_mutation is None:
            self.add_message("Chromosome Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.chromosome_mutation, str):
            self.add_message("Chromosome Mutation must be type str!")
            rslt &= False  
        elif  self.options.chromosome_mutation not in definitions.CHROMOSOME_MUTATOR_STRINGS:
            self.add_message("Invalid value of Chromosome Mutation: {0}. Allowed values: {1}".format(self.options.chromosome_mutation, self.get_allowed_values(definitions.CHROMOSOME_MUTATOR_STRINGS)))
            rslt &= False   
        if self.options.exit_check is None:
            self.add_message("Exit Check must not be None!")
            rslt &= False
        elif not isinstance(self.options.exit_check, str):
            self.add_message("Exit Check must be type str!")
            rslt &= False
        elif self.options.exit_check not in definitions.EXIT_CRITERIA_STRINGS:
            self.add_message("Invalid value of Exit Check: {0}. Allowed values: {1}".format(self.options.exit_check, self.get_allowed_values(definitions.EXIT_CRITERIA_STRINGS)))
            rslt &= False
        if self.options.chromosome_mutation == definitions.CROSS_DIVERSITY:
            if self.options.cross_diversity_mutation_gene_selection is None:
                self.add_message("Cross Diversity Mutation Gene Selection must not be None!")
                rslt &= False
            elif not isinstance(self.options.cross_diversity_mutation_gene_selection, str):
                self.add_message("Cross Diversity Mutation Gene Selection must be type str!")
                rslt &= False
            elif not self.validate_selection(self.options.cross_diversity_mutation_gene_selection, "Cross Diversity Mutation Gene Selection", self.options.number_of_mutation_genes, "Group Size for Cross Diversity Mutation Gene Selection must be below or equal than the number of mutation variables!"):
                rslt &= False           
        if self.options.logging is None:
            self.add_message("Logging must not be None!")
            rslt &= False
        elif not isinstance(self.options.logging, bool):
            self.add_message("Logging must be type bool!")
            rslt &= False        
        if self.options.must_mutate_for_same_parents is None:
            self.add_message("Must Mutate For Same Parents must not be None!")
            rslt &= False
        elif not isinstance(self.options.must_mutate_for_same_parents, bool):
            self.add_message("Must Mutate For Same Parents must be type bool!")
            rslt &= False 
        if self.options.population_mutation == definitions.COST_DIVERSITY or definitions.PARENTS_DIVERSITY in self.options.population_mutation:
            if self.options.parent_diversity_mutation_chromosome_selection is None:
                self.add_message("Parent Diversity Mutation Chromosome Selection must not be None!")
                rslt &= False
            elif not isinstance(self.options.parent_diversity_mutation_chromosome_selection, str):
                self.add_message("Parent Diversity Mutation Chromosome Selection must be type str!")
                rslt &= False
            elif not self.validate_selection(self.options.parent_diversity_mutation_chromosome_selection, "Parents Diversity Mutation Chromosome Selection", (population_size // 2) - self.options.immigration_number, "Group Size for Parents Diversity Mutation Chromosome Selection cannot have the value below half population!"):
                rslt &= False 
        if self.options.population_mutation is None:
            self.add_message("Population Mutation must not be None!")
            rslt &= False
        elif not isinstance(self.options.population_mutation, str):
            self.add_message("Population Mutation must be type str!")
            rslt &= False
        elif definitions.PARAM_SEPARATOR in self.options.population_mutation:
            mutator_strings = [ms.strip() for ms in self.options.population_mutation.split(definitions.PARAM_SEPARATOR)]
            for mutator_string in mutator_strings:
                if mutator_string not in definitions.POPULATION_MUTATOR_STRINGS:
                    self.add_message("Invalid value of Population Mutation: {0}. Allowed values: {1}".format(mutator_string, self.get_allowed_values(definitions.POPULATION_MUTATOR_STRINGS)))
                    rslt &= False
        elif self.options.population_mutation not in definitions.POPULATION_MUTATOR_STRINGS:
            self.add_message("Invalid value of Population Mutation: {0}. Allowed values: {1}".format(self.options.population_mutation, self.get_allowed_values(definitions.POPULATION_MUTATOR_STRINGS)))
            rslt &= False
        if self.options.parent_selection is None:
            self.add_message("Parent Selection must not be None!")
            rslt &= False
        elif not isinstance(self.options.parent_selection, str):
            self.add_message("Parent Selection must be type str!")
            rslt &= False
        elif not self.validate_selection(self.options.parent_selection, "Parent Selection", (population_size // 2) - self.options.immigration_number, "Group Size for parent selection cannot have the value below half population!"):
            rslt &= False       
        if self.options.requested_cost is None:
            self.add_message("Requested Cost must not be None!")
            rslt &= False
        elif not isinstance(self.options.requested_cost, float):
            self.add_message("Requested Cost must be type float!")
            rslt &= False
        if self.options.timeout is None:
            self.add_message("Timeout must not be None!")
            rslt &= False
        elif not isinstance(self.options.timeout, int):
            self.add_message("Timeout must be type int!")
            rslt &= False
        elif self.options.timeout < 1:
            self.add_message("Invalid timeout value: {0}".format(str(self.options.timeout)))
            rslt &= False
        return rslt
    
    def validate_selection(self, selection_string, selection_type, comparing_number, group_size_error_message) -> bool:
        selection_strings = selection_string.split(definitions.PARAM_SEPARATOR)
        if len(selection_strings) > 2 or (len(selection_strings) > 1 and selection_strings[0] != definitions.TOURNAMENT):
            self.add_message("Invalid {0} value: {1}".format(selection_type, selection_string))
            return False
        if selection_strings[0] == definitions.TOURNAMENT and len(selection_strings) > 1:
            group_size= selection_strings[1]
            n_group_size = -1
            try:
                n_group_size = int(group_size)
            except:
                self.add_message("Invalid {0} value: {1}".format(selection_type, selection_string))
                return False
            if n_group_size < 2:
                self.add_message("Invalid {0} value: {1}. Minimal group size is 2.".format(selection_type, selection_string))
                return False
            if not isinstance(n_group_size, int):
                self.add_message("Invalid value for {0}: {1}".format(selection_type, selection_string))
                return False
            elif int(n_group_size) > comparing_number:
                self.add_message(group_size_error_message)
                return False
        if not selection_strings[0] in definitions.SELECTION_STRINGS:
            self.add_message("Invalid {0} value: {1}. Allowed values: {2}".format(selection_type, selection_string, self.get_allowed_values(definitions.SELECTION_STRINGS)))
            return False
        return True
    
    def get_allowed_values(self, s_list):
        rslt = ""
        for s in s_list:
            rslt += s + ", "
        return rslt[:-2]