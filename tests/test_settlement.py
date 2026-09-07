"""
Unit tests for the Split Expenses settlement logic and edge cases.
"""
import unittest
import json
from app.settlement import calculate_settlements, _minimize_transactions_cents


class MockMember:
    def __init__(self, member_id, name):
        self.id = member_id
        self.name = name


class MockExpense:
    def __init__(self, paid_by_id, amount, split_among):
        self.paid_by_id = paid_by_id
        self.amount = amount
        self.split_among = json.dumps(split_among) if isinstance(split_among, list) else split_among


class TestSettlementLogic(unittest.TestCase):

    def setUp(self):
        self.m1 = MockMember(1, 'Alice')
        self.m2 = MockMember(2, 'Bob')
        self.m3 = MockMember(3, 'Charlie')
        self.m4 = MockMember(4, 'David')
        self.members = [self.m1, self.m2, self.m3, self.m4]

    def test_equal_split_three_people(self):
        """Test $100 split 3 ways — verifies cent remainder distribution and 0 floating point drift."""
        e1 = MockExpense(1, 100.0, [1, 2, 3])
        res = calculate_settlements([self.m1, self.m2, self.m3], [e1])

        self.assertEqual(res['total_spent'], 100.0)
        net_sum = sum(b['net'] for b in res['balances'])
        self.assertAlmostEqual(net_sum, 0.0, places=2)

        total_settlement = sum(s['amount'] for s in res['settlements'])
        self.assertEqual(round(total_settlement, 2), 66.66)

    def test_payer_excluded_from_split(self):
        """Test scenario where Alice pays $50 for Bob & Charlie, but Alice is excluded from split."""
        e1 = MockExpense(1, 50.0, [2, 3])
        res = calculate_settlements([self.m1, self.m2, self.m3], [e1])

        self.assertEqual(res['balances'][0]['paid'], 50.0)
        self.assertEqual(res['balances'][0]['owed'], 0.0)
        self.assertEqual(res['balances'][0]['net'], 50.0)

        # Bob & Charlie each owe $25 to Alice
        self.assertEqual(len(res['settlements']), 2)
        total_recieved = sum(s['amount'] for s in res['settlements'] if s['to_id'] == 1)
        self.assertEqual(total_recieved, 50.0)

    def test_single_member_group(self):
        """Test 1-person group adding an expense."""
        e1 = MockExpense(1, 45.50, [1])
        res = calculate_settlements([self.m1], [e1])

        self.assertEqual(res['total_spent'], 45.50)
        self.assertEqual(res['balances'][0]['net'], 0.0)
        self.assertEqual(len(res['settlements']), 0)

    def test_large_amounts(self):
        """Test large financial values ($1,000,000.00)."""
        e1 = MockExpense(1, 1000000.00, [1, 2, 3, 4])
        res = calculate_settlements(self.members, [e1])

        self.assertEqual(res['total_spent'], 1000000.00)
        self.assertEqual(res['balances'][0]['net'], 750000.00)
        self.assertEqual(len(res['settlements']), 3)

    def test_circular_debts_cancel_out(self):
        """Test circular spending where A pays for B, B pays for C, C pays for A."""
        e1 = MockExpense(1, 30.0, [1, 2])
        e2 = MockExpense(2, 30.0, [2, 3])
        e3 = MockExpense(3, 30.0, [3, 1])

        res = calculate_settlements([self.m1, self.m2, self.m3], [e1, e2, e3])

        self.assertEqual(res['total_spent'], 90.0)
        for b in res['balances']:
            self.assertEqual(b['net'], 0.0)
        self.assertEqual(len(res['settlements']), 0)

    def test_invalid_payer_id(self):
        """Test expense with non-existent payer ID is skipped gracefully."""
        e1 = MockExpense(999, 50.0, [1, 2])
        res = calculate_settlements([self.m1, self.m2], [e1])

        self.assertEqual(res['total_spent'], 0.0)
        for b in res['balances']:
            self.assertEqual(b['net'], 0.0)

    def test_invalid_split_member_id(self):
        """Test expense referencing deleted/invalid split ID."""
        e1 = MockExpense(1, 60.0, [1, 2, 999])
        res = calculate_settlements([self.m1, self.m2], [e1])

        self.assertEqual(res['total_spent'], 60.0)
        self.assertEqual(res['balances'][0]['owed'], 30.0)
        self.assertEqual(res['balances'][1]['owed'], 30.0)

    def test_empty_expenses(self):
        """Test group with no expenses."""
        res = calculate_settlements(self.members, [])
        self.assertEqual(res['total_spent'], 0.0)
        self.assertEqual(len(res['settlements']), 0)


if __name__ == '__main__':
    unittest.main()
