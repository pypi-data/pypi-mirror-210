import requests
from .api_interface import APIInteface


class ConfigAPIinterface(APIInteface):
    def __init__(self, domain: str = "https://safe-config.safe.global"):
        super().__init__(domain, "config_svc", "v1")

    def get_chains(self):
        res = requests.get(f"{self.base_url}/chains")
        return res.json().get("results")

    def get_supported_chain_ids(self):
        chains = self.get_chains()
        return [x.get('chainId') for x in chains]

    def get_transaction_api_url_for_chain(self, chain_id: int):
        res = requests.get(f"{self.base_url}/chains/{chain_id}/")
        return res.json().get("transactionService")