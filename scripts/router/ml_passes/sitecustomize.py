# -*- coding: utf-8 -*-
"""Shift every integer random seed by SEED_OFFSET so the existing generators produce different variants."""
import os
import random

_off = int(os.environ.get("SEED_OFFSET", "0"))
if _off:
    _STEP = 1000003
    _seed_method = random.Random.seed

    def _seed(self, a=None, version=2):
        if isinstance(a, int) and not isinstance(a, bool):
            a = a + _off * _STEP
        return _seed_method(self, a, version)

    random.Random.seed = _seed
    _module_seed = random.seed

    def _module_seed_wrapper(a=None, version=2):
        if isinstance(a, int) and not isinstance(a, bool):
            a = a + _off * _STEP
        return _module_seed(a, version)

    random.seed = _module_seed_wrapper
    _module_seed_wrapper(_off)
