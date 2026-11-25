"""Unit tests for :mod:`expert_system.fact_base`."""

import unittest

from expert_system.fact_base import FactBase


class TestFactBaseNormalisation(unittest.TestCase):
    def test_normalise_trims_collapses_and_lowercases(self):
        self.assertEqual(FactBase.normalise("  Sore    THROAT "), "sore throat")

    def test_normalise_rejects_non_string(self):
        with self.assertRaises(TypeError):
            FactBase.normalise(42)  # type: ignore[arg-type]

    def test_normalise_rejects_empty(self):
        with self.assertRaises(ValueError):
            FactBase.normalise("   ")


class TestFactBaseMutations(unittest.TestCase):
    def test_add_returns_true_then_false_on_duplicate(self):
        fb = FactBase()
        self.assertTrue(fb.add("Fever"))
        self.assertFalse(fb.add(" fever "))

    def test_add_many_counts_only_new(self):
        fb = FactBase(["fever", "cough"])
        self.assertEqual(fb.add_many(["cough", "headache", "FEVER"]), 1)
        self.assertEqual(len(fb), 3)

    def test_contains_and_in_operator_are_case_insensitive(self):
        fb = FactBase(["fever"])
        self.assertTrue(fb.contains("FEVER"))
        self.assertIn(" fever ", fb)

    def test_contains_returns_false_for_non_string(self):
        fb = FactBase(["fever"])
        self.assertNotIn(123, fb)

    def test_snapshot_is_immutable(self):
        fb = FactBase(["fever"])
        snapshot = fb.snapshot()
        fb.add("cough")
        self.assertNotIn("cough", snapshot)
        self.assertIsInstance(snapshot, frozenset)

    def test_iteration_is_sorted(self):
        fb = FactBase(["cough", "fever", "ache"])
        self.assertEqual(list(fb), ["ache", "cough", "fever"])


if __name__ == "__main__":
    unittest.main()
