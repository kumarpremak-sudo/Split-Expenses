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
    def __init__(self, paid_by_id, amount, split_among, entry_type='expense'):
        self.paid_by_id = paid_by_id
        self.amount = amount
        self.split_among = json.dumps(split_among) if isinstance(split_among, list) else split_among
        self.entry_type = entry_type


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

    def test_advance_collection_equal(self):
        """Test Alice collecting $1,000 advance from Alice, Bob, Charlie, David ($4,000 total)."""
        e1 = MockExpense(1, 4000.0, [1, 2, 3, 4], entry_type='advance')
        res = calculate_settlements(self.members, [e1])

        # Advance collection must NOT inflate total group spending
        self.assertEqual(res['total_spent'], 0.0)

        balances = {b['id']: b for b in res['balances']}
        self.assertEqual(balances[1]['net'], -3000.0)  # Alice holds $3,000 pool cash
        self.assertEqual(balances[2]['net'], 1000.0)   # Bob pre-paid $1,000
        self.assertEqual(balances[3]['net'], 1000.0)   # Charlie pre-paid $1,000
        self.assertEqual(balances[4]['net'], 1000.0)   # David pre-paid $1,000

        # Alice pays back Bob, Charlie, and David $1,000 each
        self.assertEqual(len(res['settlements']), 3)
        for s in res['settlements']:
            self.assertEqual(s['from_id'], 1)  # From Alice
            self.assertEqual(s['amount'], 1000.0)

    def test_advance_collection_followed_by_group_expense(self):
        """Test $4,000 advance collection followed by $2,000 Food expense paid by Alice from pool."""
        adv = MockExpense(1, 4000.0, [1, 2, 3, 4], entry_type='advance')
        food = MockExpense(1, 2000.0, [1, 2, 3, 4], entry_type='expense')
        res = calculate_settlements(self.members, [adv, food])

        # Total spent should only count actual expense ($2,000.00)
        self.assertEqual(res['total_spent'], 2000.0)

        balances = {b['id']: b for b in res['balances']}
        # Fair share per person = $500
        # Bob, Charlie, David contributed $1,000 advance - $500 fair share = +$500 net
        self.assertEqual(balances[2]['net'], 500.0)
        self.assertEqual(balances[3]['net'], 500.0)
        self.assertEqual(balances[4]['net'], 500.0)

        # Alice held $3,000 cash - spent $2,000 + $500 fair share = -$1,500 net
        self.assertEqual(balances[1]['net'], -1500.0)

    def test_partial_split_exclusion(self):
        """Test expense paid by Alice ($150) split ONLY among Bob and Charlie (Alice excluded)."""
        food = MockExpense(1, 150.0, [2, 3], entry_type='expense')
        res = calculate_settlements([self.m1, self.m2, self.m3], [food])

        self.assertEqual(res['total_spent'], 150.0)
        balances = {b['id']: b for b in res['balances']}
        self.assertEqual(balances[1]['paid'], 150.0)
        self.assertEqual(balances[1]['owed'], 0.0)
        self.assertEqual(balances[1]['net'], 150.0)
        self.assertEqual(balances[2]['owed'], 75.0)
        self.assertEqual(balances[2]['net'], -75.0)
        self.assertEqual(balances[3]['owed'], 75.0)
        self.assertEqual(balances[3]['net'], -75.0)

        # Bob and Charlie pay Alice $75 each
        self.assertEqual(len(res['settlements']), 2)
        total_settlement = sum(s['amount'] for s in res['settlements'])
        self.assertEqual(total_settlement, 150.0)

    def test_zero_valid_splitters(self):
        """Test expense with empty split list defaults to all valid group members."""
        food = MockExpense(1, 100.0, [], entry_type='expense')
        res = calculate_settlements([self.m1, self.m2], [food])

        self.assertEqual(res['total_spent'], 100.0)
        balances = {b['id']: b for b in res['balances']}
        self.assertEqual(balances[1]['owed'], 50.0)
    def test_null_amount_handled_gracefully(self):
        """Test expense with None or 0 amount is skipped without crashing."""
        e1 = MockExpense(1, None, [1, 2])
        e2 = MockExpense(1, 0.0, [1, 2])
        res = calculate_settlements([self.m1, self.m2], [e1, e2])

        self.assertEqual(res['total_spent'], 0.0)
        self.assertEqual(len(res['settlements']), 0)


if __name__ == '__main__':
    unittest.main()

