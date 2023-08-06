from typing import List
from gadapt.ga_model.ranking_model import RankingModel
import gadapt.ga_model.definitions as definitions
class BaseSampling:
    def get_sample(self, lst: List[RankingModel], max_num, sort_key=None) -> List[RankingModel]:
        if len(lst) == 0:
            return lst
        for m in lst:
            m.reset_for_sampling()
        if max_num < 1 or max_num > len(lst):
            self.max_num = len(lst)
        else:
            self.max_num = max_num
        self.sort_key = sort_key
        return self.prepare_sample(lst)
    
    def prepare_sample(self, lst: List[RankingModel]) -> List[RankingModel]:
        raise Exception(definitions.NOT_IMPLEMENTED)