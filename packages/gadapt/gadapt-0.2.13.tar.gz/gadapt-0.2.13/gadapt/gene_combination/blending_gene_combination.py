import random
from gadapt.ga_model.gene import Gene
from gadapt.gene_combination.base_gene_combination import BaseGeneCombination

class BlendingGeneCombination(BaseGeneCombination):
    def combine(self, mother_gene: Gene, father_gene: Gene):
        genetic_variable = father_gene.genetic_variable
        val_father = father_gene.variable_value
        val_mother = mother_gene.variable_value
        x = 1
        if val_mother > val_father:
            x = -1
        beta_steps = random.randint(0, round(abs((val_father - val_mother) / genetic_variable.step)))
        val1 = round(val_father - (beta_steps * x) * genetic_variable.step, genetic_variable.decimal_places)
        val2 = round(val_mother + (beta_steps * x) * genetic_variable.step, genetic_variable.decimal_places)
        return val1, val2
        
