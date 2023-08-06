import requests


class EtherscanAPIInterface:
    def __init__(self, domain: str = "https://api.etherscan.io", api_key: str = "YourApiKeyToken"):
        self.base_url = f"{domain}/api"
        self.api_key = api_key

    def get_contract_creation(self, contract_addresses: list):
        results = []
        for i in range(0, len(contract_addresses), 5):
            batch = contract_addresses[i:i+5]
            addresses_str = ','.join(batch)

            params = {
                "module": "contract",
                "action": "getcontractcreation",
                "contractaddresses": addresses_str,
                "apikey": self.api_key
            }
            res = requests.get(self.base_url, params=params)
            data = res.json()

            if data.get("status") == "1" and data.get("message") == "OK":
                parsed_results = [
                    {
                        "contractAddress": item.get("contractAddress"),
                        "contractCreator": item.get("contractCreator"),
                        "txHash": item.get("txHash")
                    } for item in data.get("result", [])
                ]
                results.extend(parsed_results)

        return results

    def get_block_number_by_hash(self, tx_hash: str):
        params = {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": tx_hash,
            "apikey": self.api_key
        }
        res = requests.get(self.base_url, params=params)
        data = res.json()
        
        if data.get("result"):
            block_number = int(data["result"]["blockNumber"], 16)  # Convert hex string to integer
            return block_number
        else:
            return None
        
    def map_address_block_creation(self, contract_addresses: list):
        creation_data = self.get_contract_creation(contract_addresses)
        address_block_dict = {}

        for item in creation_data:
            address = item["contractAddress"]
            tx_hash = item["txHash"]
            block_number = self.get_block_number_by_hash(tx_hash)

            address_block_dict[address] = block_number

        # Sort address_block_dict by decreasing block number
        sorted_address_block_dict = dict(sorted(address_block_dict.items(), key=lambda item: item[1], reverse=True))

        return sorted_address_block_dict
