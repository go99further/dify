import unittest

from eval.workflow_contract import CASES, execute


class WorkflowContractTest(unittest.TestCase):
    def test_all_replay_cases_match_expected_outcome(self):
        failures = []
        for case in CASES:
            actual = execute(case)["outcome"]
            if actual != case["expected"]:
                failures.append((case["id"], case["expected"], actual))
        self.assertEqual([], failures)

    def test_security_cases_never_call_tools(self):
        for case in CASES:
            if case["intent"] == "security_refusal":
                self.assertIn(execute(case)["outcome"], {"refuse_private_key", "refuse_policy"})


if __name__ == "__main__":
    unittest.main()
