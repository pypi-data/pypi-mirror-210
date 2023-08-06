
from functools import reduce
import math
import random
from typing import List
import gadapt.ga_model.definitions as definitions
def get_rand_bool():
    rand_int = random.getrandbits(1)
    return bool(rand_int)

def get_rand_bool_with_probability(f: float):
    r = random.uniform(0, 1)
    if r <= f:
        return True
    return False

def average(lst: List):
    return reduce(lambda a, b: a + b, lst) / len(lst)

def try_get_int(s):
    if isinstance(s, int):
        return s
    if isinstance(s, str):
        try:
            n = int(s)
            return n
        except:
            return s
    return s

def try_get_float(s):
    if isinstance(s, float):
        return s
    if isinstance(s, str):
        try:
            n = float(s)
            return n
        except:
            return s
    return s

def try_get_bool(s):
    if isinstance(s, bool):
        return s
    if isinstance(s, str):
        try:
            n = bool(s)
            return n
        except:
            return s
    return s

def prepare_string(s: str):
    str = s
    while " " in str or "\n" in str:
        str = str.replace(" ", "").replace("\n", "")
    return str