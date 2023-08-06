import random
from typing import List
from gadapt.ga_model.ranking_model import RankingModel
from gadapt.sampling.base_sampling import BaseSampling

class RouletteWheelSampling(BaseSampling):
    
    def prepare_sample(self, lst: List[RankingModel]) -> List[RankingModel]:
        rank_sum = sum(range(1, len(lst) + 1))
        cummultative_probability_list: List[float] = []
        cummulative_probability = 0.0
        n_keep = len(lst)
        for j in range(len(lst)):
            n = n_keep - j
            probability_for_action = float(n_keep - n + 1) / float(rank_sum)
            cummulative_probability += probability_for_action
            cummultative_probability_list.append(cummulative_probability)
        rank = 0
        unallocated_members = [rm for rm in lst]
        unallocated_members.sort(key = self.sort_key, reverse=True)        
        members_for_action = []
        for j in range(self.max_num):
            if len(unallocated_members) == 0:
                continue
            i_c_p_l = 0
            for i_c_p_l, m in enumerate(unallocated_members):
                m.cummulative_probability = cummultative_probability_list[i_c_p_l]
            rnd_value = random.random()
            max_prob = (max(unallocated_members, key=lambda m: m.cummulative_probability)).cummulative_probability
            rnd_value = rnd_value*max_prob
            mem = next(mb for mb in unallocated_members if mb.cummulative_probability >= rnd_value)
            if not mem is None:
                rank += 1
                mem.rank = rank
                members_for_action.append(mem)
            unallocated_members = [um for um in unallocated_members if um.rank == -1]
        members_for_action.sort(key=lambda g: g.rank)
        return members_for_action