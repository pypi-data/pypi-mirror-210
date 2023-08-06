from typing import List, Tuple
from gadapt.ga_model.chromosome import Chromosome
import gadapt.ga_model.definitions as definitions

class BaseParentSelector:    
    def select_mates(self, population) -> List[Tuple[Chromosome, Chromosome]]:
        raise Exception(definitions.NOT_IMPLEMENTED)