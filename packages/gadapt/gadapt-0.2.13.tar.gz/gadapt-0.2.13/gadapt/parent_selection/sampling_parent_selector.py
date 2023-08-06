from typing import List, Tuple
from gadapt.ga_model.chromosome import Chromosome
from gadapt.parent_selection.base_parent_selector import BaseParentSelector
from gadapt.sampling.base_sampling import BaseSampling


class SamplingParentSelector(BaseParentSelector):

    def __init__(self, sampling: BaseSampling) -> None:
        super().__init__()
        self.sampling = sampling

    def select_mates(self, population) -> List[Tuple[Chromosome, Chromosome]]:
        working_chromosomes = self.sampling.get_sample(
            population.chromosomes, len(population), lambda c: c.cost_value)
        list_of_mates: List[Tuple[Chromosome, Chromosome]] = []
        while len(working_chromosomes) > 1:
            c1 = working_chromosomes.pop(0)
            c2 = working_chromosomes.pop(0)
            list_of_mates.append((c1, c2))
        return list_of_mates
