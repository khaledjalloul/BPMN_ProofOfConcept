import json
import time
from typing import Tuple


def load_constraints() -> dict:
    with open('data/constraints.json') as f:
        constraints = json.load(f)
    return constraints


def load_alternatives(in_batches: bool) -> Tuple[list, float]:
    if in_batches:
        with open('data/generated_alternatives.json') as f:
            alternatives_arr = json.load(f)
        alternatives = {}
        for alternatives_batch in alternatives_arr:
            alternatives.update(alternatives_batch)
    else:
        with open('data/generated_alternatives.json') as f:
            alternatives = json.load(f)

    return alternatives, time.time()
