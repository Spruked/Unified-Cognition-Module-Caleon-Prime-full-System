# echostack_module/tests/ethics_trace_test.py

"""
Ethics Trace Test
Validates ethical reasoning traceability using seed overlays and principle filters.
"""

import unittest
from echostack_module.core_principles import get_principle
from echostack_module.echo_core import process_echo

class EthicsTraceTest(unittest.TestCase):

    def test_spinoza_conatus_trace(self):
        payload = "Every being strives to persist in its own nature."
        trace = process_echo(payload)
        self.assertIn("spinoza", str(trace).lower())
        self.assertIn("principle_used", trace)
        self.assertTrue(trace["logic_filter"])

    def test_hume_is_ought_detection(self):
        payload = "You cannot derive an 'ought' from an 'is'."
        trace = process_echo(payload)
        self.assertIn("hume", str(trace).lower())
        self.assertIn("epistemic_overlay", trace)
        self.assertTrue("is-ought" in str(trace).lower())

    def test_apriori_law_of_identity(self):
        principle = get_principle("law_of_identity")
        self.assertEqual(principle["definition"], "Every object is identical to itself; A is A.")

    def test_contradiction_detection(self):
        payload = "It is raining and not raining at the same time."
        trace = process_echo(payload)
        self.assertIn("contradiction", str(trace).lower())
        self.assertEqual(trace["trace_metadata"].get("consistency"), False)

if __name__ == "__main__":
    unittest.main()
