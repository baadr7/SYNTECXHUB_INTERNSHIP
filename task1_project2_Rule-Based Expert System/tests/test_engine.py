"""Unit tests for :mod:`expert_system.engine` (forward chaining)."""

import unittest

from expert_system.engine import InferenceEngine
from expert_system.knowledge_loader import KnowledgeBase
from expert_system.rule import Rule


def make_kb(*rules: Rule) -> KnowledgeBase:
    return KnowledgeBase(list(rules))


class TestForwardChaining(unittest.TestCase):
    def test_single_step_inference(self):
        kb = make_kb(Rule("R1", ["fever", "cough"], "flu"))
        result = InferenceEngine(kb).infer(["fever", "cough"])
        self.assertEqual(result.derived_facts, ["flu"])
        self.assertTrue(result.reached)
        self.assertEqual(result.fired_rule_ids, ["R1"])

    def test_multi_step_chaining(self):
        kb = make_kb(
            Rule("R1", ["a", "b"], "c"),
            Rule("R2", ["c", "d"], "e"),
            Rule("R3", ["e"], "f"),
        )
        result = InferenceEngine(kb).infer(["a", "b", "d"])
        self.assertEqual(result.fired_rule_ids, ["R1", "R2", "R3"])
        self.assertIn("f", result.final_facts)

    def test_no_rule_fires_on_unrelated_facts(self):
        kb = make_kb(Rule("R1", ["fever", "cough"], "flu"))
        result = InferenceEngine(kb).infer(["headache"])
        self.assertFalse(result.reached)
        self.assertEqual(result.derived_facts, [])
        self.assertEqual(result.steps, [])

    def test_rule_fires_at_most_once(self):
        kb = make_kb(Rule("R1", ["fever"], "flu"))
        result = InferenceEngine(kb).infer(["fever"])
        self.assertEqual(result.fired_rule_ids.count("R1"), 1)

    def test_determinism_across_runs(self):
        kb = make_kb(Rule("R1", ["a"], "b"), Rule("R2", ["b"], "c"))
        engine = InferenceEngine(kb)
        first = engine.infer(["a"])
        second = engine.infer(["a"])
        self.assertEqual(first.final_facts, second.final_facts)
        self.assertEqual(first.fired_rule_ids, second.fired_rule_ids)

    def test_empty_initial_facts_yield_no_steps(self):
        kb = make_kb(Rule("R1", ["a"], "b"))
        result = InferenceEngine(kb).infer([])
        self.assertEqual(result.steps, [])
        self.assertFalse(result.reached)

    def test_string_input_is_rejected(self):
        kb = make_kb(Rule("R1", ["a"], "b"))
        with self.assertRaises(TypeError):
            InferenceEngine(kb).infer("a")

    def test_invalid_max_iterations_rejected(self):
        kb = make_kb(Rule("R1", ["a"], "b"))
        with self.assertRaises(ValueError):
            InferenceEngine(kb, max_iterations=0)


class TestTraceableSteps(unittest.TestCase):
    def test_steps_capture_iteration_and_description(self):
        kb = make_kb(Rule("R1", ["a"], "b", description="a implies b"))
        result = InferenceEngine(kb).infer(["a"])
        step = result.steps[0]
        self.assertEqual(step.rule_id, "R1")
        self.assertEqual(step.antecedents, ("a",))
        self.assertEqual(step.consequent, "b")
        self.assertEqual(step.description, "a implies b")
        self.assertGreaterEqual(step.iteration, 1)


if __name__ == "__main__":
    unittest.main()