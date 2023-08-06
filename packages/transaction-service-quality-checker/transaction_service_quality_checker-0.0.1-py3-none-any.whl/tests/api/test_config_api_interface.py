import unittest
from transaction_service_quality_checker.api.config_api_interface import ConfigAPIinterface

class ConfigAPIInterfaceTest(unittest.TestCase):
    config = ConfigAPIinterface()

    def test_is_healthy(self):
        res = self.config.is_healthy()
        self.assertIsInstance(res, bool)
        self.assertTrue(res)

    def test_get_chains(self):
        chains = self.config.get_chains()
        self.assertTrue(len(chains) > 0)

    def test_get_supported_chain_ids(self):
        chain_ids = self.config.get_supported_chain_ids()
        self.assertTrue(len(chain_ids) > 0)
        for value in chain_ids:
            self.assertIsInstance(value, str)
            self.assertIsInstance(int(value), int)

    def test_get_transaction_api_url_for_chain(self):
        url = self.config.get_transaction_api_url_for_chain(1)
        self.assertIsInstance(url, str)
        self.assertEqual(url, "https://safe-transaction-mainnet.safe.global")
