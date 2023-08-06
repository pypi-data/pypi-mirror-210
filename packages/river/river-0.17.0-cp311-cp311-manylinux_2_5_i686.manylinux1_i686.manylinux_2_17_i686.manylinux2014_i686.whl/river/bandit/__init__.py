"""Multi-armed bandit (MAB) policies.

The bandit policies in River are meant to have a generic API. This allows them to be used in a
variety of contexts. Within River, they are used for model selection
(see `model_selection.BanditRegressor`).

"""
from __future__ import annotations

from . import base, envs
from .epsilon_greedy import EpsilonGreedy
from .evaluate import evaluate
from .exp3 import Exp3
from .thompson import ThompsonSampling
from .ucb import UCB

__all__ = ["base", "envs", "evaluate", "EpsilonGreedy", "Exp3", "ThompsonSampling", "UCB"]
