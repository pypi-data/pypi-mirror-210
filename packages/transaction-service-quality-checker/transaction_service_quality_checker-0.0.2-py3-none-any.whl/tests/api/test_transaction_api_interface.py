import unittest
from transaction_service_quality_checker.api.transaction_api_interface import TransactionAPIinterface

class TransactionAPIInterfaceTest(unittest.TestCase):
    transactions_mainnet_api = TransactionAPIinterface(domain="https://safe-transaction-mainnet.safe.global/")

    def test_is_healthy(self):
        res = self.transactions_mainnet_api.is_healthy()
        self.assertIsInstance(res, bool)
        self.assertTrue(res)

    def test_get_safe(self):
        safe_address = "0xcA771eda0c70aA7d053aB1B25004559B918FE662"
        safe = self.transactions_mainnet_api.get_safe(safe_address)
        self.assertIsInstance(safe, object)
        self.assertEqual(safe.get("address"), safe_address)

    def test_get_transactions_from_safe(self):
        safe_address = "0xcA771eda0c70aA7d053aB1B25004559B918FE662"
        transactions = self.transactions_mainnet_api.get_transactions_from_safe(safe_address)
        self.assertIsInstance(transactions, object)
        self.assertIsInstance(transactions['count'], int)
        self.assertIsInstance(transactions['results'], object)
        self.assertIsInstance(len(transactions['results']), int)

    def test_get_all_transactions_from_safe(self):
        safe_address = "0xcA771eda0c70aA7d053aB1B25004559B918FE662"
        transactions = self.transactions_mainnet_api.get_complete_list_of_transactions_from_safe(safe_address)
        self.assertIsInstance(transactions, object)
        self.assertIsInstance(len(transactions), int)

    def test_get_balances_for_safe(self):
        safe_address = "0xcA771eda0c70aA7d053aB1B25004559B918FE662"
        balances = self.transactions_mainnet_api.get_balances_for_safe(safe_address)
        self.assertIsInstance(balances, object)
        self.assertIsInstance(len(balances), int)
        self.assertIsInstance(balances[0]["balance"], str)

    def test_get_balances_in_usd_for_safe(self):
        safe_address = "0xcA771eda0c70aA7d053aB1B25004559B918FE662"
        balances_in_usd = self.transactions_mainnet_api.get_balances_in_usd_for_safe(safe_address)
        self.assertIsInstance(balances_in_usd, object)
        self.assertIsInstance(len(balances_in_usd), int)
        self.assertIsInstance(balances_in_usd[0]["balance"], str)
        self.assertIsInstance(balances_in_usd[0]["fiatBalance"], str)

