"""Unit tests for :mod:`expert_system.rule`."""

import unittest

from expert_system.rule import Rule


class TestRuleValidation(unittest.TestCase):
    def test_empty_id_is_rejected(self):
        with self.assertRaises(ValueError):
            Rule("", ["fever"], "flu")

    def test_empty_antecedents_are_rejected(self):
        with self.assertRaises(ValueError):
            Rule("R1", [], "flu")

    def test_antecedents_and_consequent_are_normalised(self):
        rule = Rule("R1", [" Fever ", "Cough"], "  Flu ")
        self.assertEqual(rule.antecedents, ("fever", "cough"))
        self.assertEqual(rule.consequent, "flu")


class TestRuleTriggering(unittest.TestCase):
    def test_is_triggered_when_all_antecedents_present(self):
        rule = Rule("R1", ["fever", "cough", "muscle aches"], "flu")
        self.assertTrue(rule.is_triggered(["fever", "cough", "muscle aches", "x"]))

    def test_not_triggered_when_one_antecedent_missing(self):
        rule = Rule("R1", ["fever", "cough", "muscle aches"], "flu")
        self.assertFalse(rule.is_triggered(["fever", "cough"]))

    def test_missing_antecedents_reports_gap(self):
        rule = Rule("R1", ["fever", "cough", "muscle aches"], "flu")
        self.assertEqual(rule.missing_antecedents(["fever"]), ["cough", "muscle aches"])


class TestRuleSerialisation(unittest.TestCase):
    def test_from_dict_and_to_dict_roundtrip(self):
        payload = {
            "id": "R1",
            "if": ["fever", "cough"],
            "then": "flu",
            "description": "febrile cough",
        }
        rule = Rule.from_dict(payload)
        self.assertEqual(rule.to_dict(), payload)

    def test_equality_and_hash_use_rule_id(self):
        rule_a = Rule("R1", ["fever"], "flu")
        rule_b = Rule("R1", ["cough"], "cold")
        self.assertEqual(rule_a, rule_b)
        self.assertEqual(len({rule_a, rule_b}), 1)


if __name__ == "__main__":
    unittest.main()