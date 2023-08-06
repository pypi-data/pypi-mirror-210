import statistics as stat
from gadapt.ga_model.genetic_variable import GeneticVariable
import gadapt.utils.ga_utils as ga_utils

class CommonVariableUpdater:
    def update_variables(self, population):
        def scale_values(gv: GeneticVariable, values):
            rslt = []
            max_val = max(values)
            diff = (gv.max_value - max_val)
            if (gv.min_value < 0):
                diff = diff - gv.min_value
            for f in values:
                rslt.append(f + diff)
            return rslt

        unique_values_per_variables = {}    
        values_per_variables = {}    
        for c in population:
            if c.is_immigrant:
                continue
            for g in c:
                unique_var_values = unique_values_per_variables.get(g.genetic_variable, None)
                var_values = values_per_variables.get(g.genetic_variable, None)
                if unique_var_values is None:
                    unique_var_values = set()
                    unique_values_per_variables[g.genetic_variable] = unique_var_values
                if (var_values is None):
                    var_values = []
                    values_per_variables[g.genetic_variable] = var_values
                unique_var_values.add(g.variable_value)
                var_values.append(g.variable_value)
        for key in unique_values_per_variables:
            if len(unique_values_per_variables[key]) == 1:
                key.stacked = True
            else:
                key.stacked = False        
        for key in values_per_variables:
            if key.stacked:
                key.relative_standard_deviation = 0.0
                continue
            scaled_values = scale_values(key, values_per_variables[key])
            stddev = stat.stdev(scaled_values)
            avg_val = ga_utils.average(scaled_values)
            rel_st_dev = stddev / avg_val
            key.relative_standard_deviation = rel_st_dev