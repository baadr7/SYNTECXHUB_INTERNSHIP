"""A transparent, rule-based expert system with forward chaining.

Public API:
    FactBase          -- working memory of known facts
    Rule              -- an if-then production rule
    KnowledgeBase     -- validated collection of rules loaded from JSON
    InferenceEngine   -- the forward-chaining reasoning engine
    InferenceResult   -- outcome of an inference run
    InferenceStep     -- a single rule activation in the trail
    Explanator        -- turns the trail into a justified reasoning path
"""

from .engine import InferenceEngine, InferenceResult, InferenceStep
from .explanation import Explanator
from .fact_base import FactBase
from .knowledge_loader import KnowledgeBase, KnowledgeBaseError
from .rule import Rule

__version__ = "1.0.0"
__all__ = [
    "FactBase",
    "Rule",
    "KnowledgeBase",
    "KnowledgeBaseError",
    "InferenceEngine",
    "InferenceResult",
    "InferenceStep",
    "Explanator",
    "__version__",
]