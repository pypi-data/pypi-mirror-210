import web3
import logging
import json
from .api.config_api_interface import ConfigAPIinterface
from .api.transaction_api_interface import TransactionAPIinterface
from metrics import Metrics
from concurrent.futures import ThreadPoolExecutor, as_completed


class Comparer():
    def __init__(self, domain_a: str, domain_b: str, log: logging.Logger = logging,
                 balance_in_usd_percentage_threshold: float = 0.03):
        self.log = log
        self.domain_a = domain_a
        self.domain_b = domain_b
        self.config_svc_a = ConfigAPIinterface(domain=domain_a)
        self.config_svc_b = ConfigAPIinterface(domain=domain_b)
        self.metrics = Metrics()
        self.web3 = web3.Web3()
        self.balance_in_usd_percentage_threshold = balance_in_usd_percentage_threshold

    def fetch_transactions(self, tx_svc: TransactionAPIinterface, address: str) -> dict:
        return tx_svc.get_transactions_from_safe(address)

    def export_metrics_to_json(self, file_path: str = "metrics.json") -> None:
        with open(file_path, "w") as outfile:
            json.dump(self.metrics.metrics, outfile, indent=4)

    def compare_safes(self, map: dict):

        categories = ["safe_metadata", "safe_transactions", "safe_balances",
                      "safe_balances_in_usd", "token_addresses_balances_in_usd"]
        for key in map["chains"].keys():
            self.compare_safes_for_chain(key, map["chains"][key])

    def compare_safes_for_chain(self, chain_id, addresses):

        categories = ["safe_metadata", "safe_transactions", "safe_balances",
                      "safe_balances_in_usd", "token_addresses_balances_in_usd"]
        key = chain_id
        # define categories for metrics
        categories_with_key = []
        for category in categories:
            category_with_key = f"{category}_{key}"
            categories_with_key.append(category_with_key)
            self.metrics.create_category(category_with_key)

        # get the transaction svc for the chain
        url_transaction_indexer_a = self.config_svc_a.get_transaction_api_url_for_chain(
            key)
        url_transaction_indexer_b = self.config_svc_b.get_transaction_api_url_for_chain(
            key)
        self.log.info(f"\n\nStart the process of comparing Safes. Domain a:  {url_transaction_indexer_a} "
                      f"and Domain b: {url_transaction_indexer_b}. \n\n***This is chain_id: {key}***")
        tx_svc_a = TransactionAPIinterface(
            domain=url_transaction_indexer_a)
        tx_svc_b = TransactionAPIinterface(
            domain=url_transaction_indexer_b)

        # Iterate over addresses and compare results
        for address in addresses:
            address = self.web3.toChecksumAddress(address)
            self.compare_safe_metadata(address=address,
                                       tx_svc_a=tx_svc_a, tx_svc_b=tx_svc_b,
                                       metrics_category=categories_with_key[0])
            self.compare_safe_transactions(address=address,
                                           tx_svc_a=tx_svc_a, tx_svc_b=tx_svc_b,
                                           metrics_category=categories_with_key[1])
            # self.compare_balances(address=address,
            #                       tx_svc_a=tx_svc_a, tx_svc_b=tx_svc_b,
            #                       metrics_category=categories_with_key[2])
            # self.compare_balances_in_usd(address=address,
            #                              tx_svc_a=tx_svc_a, tx_svc_b=tx_svc_b,
            #                              safe_metrics_category=categories_with_key[3],
            #                              token_addresses_metrics_category=categories_with_key[4])

            # Print results per blockchain
        self.log.info(
            f"\n****ANALYSIS FINALIZED FOR {key} ***\n\nPrinting summary below")
        for category_with_key in categories_with_key:
            self.log.info(
                f"\n{category_with_key}: {self.metrics.metrics[category_with_key]}")

    def compare_payloads_of_address(self, address: str, metrics_category: str,
                                    payload_a: object, payload_b: object) -> bool:
        self.metrics.increment_counter(metrics_category)
        match = True
        for field in payload_a.keys():
            if payload_a[field] != payload_b[field]:
                match = False
                self.log.debug(f"field {field} does NOT match")

        if match:
            self.log.debug(f"safe metadata of {address} is OK")
            self.metrics.increment_match(metrics_category)
        else:
            self.log.warning(f"problem in safe metadata for {address}")
            self.metrics.push_problematic_address(metrics_category, address)

    def compare_safe_metadata(self, address: str,
                              tx_svc_a: TransactionAPIinterface, tx_svc_b: TransactionAPIinterface,
                              metrics_category: str) -> None:
        self.log.info(
            f"\n\n**********\n***Compare safe metadata for address: {address}")
        res_a = tx_svc_a.get_safe(address)
        res_b = tx_svc_b.get_safe(address)
        if res_a and res_b:
            self.compare_payloads_of_address(address=address, metrics_category=metrics_category,
                                             payload_a=res_a, payload_b=res_b)
        else:
            self.log.warning(
                f"Analysis NOT done for {address} due to REST API problems")

    def compare_safe_transactions(self, address: str,
                                  tx_svc_a: TransactionAPIinterface, tx_svc_b: TransactionAPIinterface,
                                  metrics_category: str) -> None:
        self.log.debug(f"\n***Compare transactions for address: {address}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_svc = {
                executor.submit(self.fetch_transactions, tx_svc_a, address): "a",
                executor.submit(self.fetch_transactions, tx_svc_b, address): "b"
            }

            results = {}
            for future in as_completed(future_to_svc):
                svc = future_to_svc[future]
                try:
                    result = future.result()
                    results[svc] = result
                except Exception as exc:
                    self.log.error(
                        f"Fetching transactions for {address} from service {svc} failed: {exc}")

        res_a = results.get("a")
        res_b = results.get("b")

        if res_a and res_b:
            self.metrics.increment_counter(metrics_category)
            match = res_a.get("count") == res_b.get("count")

            if match:
                self.log.debug(f"Transaction count for {address} is OK")
                self.metrics.increment_match(metrics_category)
            else:
                self.log.warning(f"problem w/ transaction count for {address}. "
                                 f"We see in domain a: {res_a['count']} and in domain b: {res_b['count']}")

                self.metrics.push_problematic_address(
                    metrics_category, address)

                # TODO: Fix this, for instance disabled (concurrent call )
                # subcategory_error_prct = "error_percentage"
                # error_percentage = abs(
                #     (res_a["count"] - res_b["count"]) / res_a["count"]) if res_a["count"] > 0 else 1
                # prev_error = self.metrics.get_subcategory(
                #     metrics_category, subcategory_error_prct)
                # counter = self.metrics.get_counter(metrics_category)
                # error_percentage = (
                #     (prev_error * (counter - 1)) + error_percentage) / counter
                # self.metrics.set_subcategory(
                #     metrics_category, subcategory_error_prct, error_percentage)
        else:
            self.log.warning(
                f"Analysis NOT done for {address} due to REST API problems")

    def _generate_token_map(self, token_list: list, field_as_value: str = "balance") -> dict:
        token_map = {}
        if not isinstance(token_list, list) and isinstance(token_list.get("code"), int):
            raise ValueError(
                f"Error since token_list is not a list and we got error code {token_list.get('code')} w/ message "
                f"{token_list.get('message')}")
        for t in token_list:
            if t is dict and t.get("tokenAddress") is None:
                t["tokenAddress"] = "1"  # ETH is none so we make it 1
            token_map[t["tokenAddress"]] = t.get(field_as_value)
        return token_map

    def _compare_balances_payloads(self, address: str, res_a, res_b, metrics_category: str) -> bool:
        if res_a and res_b:
            self.metrics.increment_counter(metrics_category)
            token_map_a = self._generate_token_map(res_a)
            token_map_b = self._generate_token_map(res_b)

            match = True
            for token in res_a:
                token_addr = token["tokenAddress"] or "1"  # in case is Ether
                self.log.debug(
                    f"\nBalance for token address {token_addr} in domain a: {token_map_a.get(token_addr)} and in "
                    f"domain b {token_map_b.get(token_addr)}")
                if token_map_a.get(token_addr) != token_map_b.get(token_addr):
                    self.log.warning(
                        f"Balance for token address {token_addr} does NOT match")
                    match = False
                else:
                    self.log.debug(
                        f"Balance for token address {token_addr} is OK")
            self.metrics.increment_match(metrics_category) if match \
                else self.metrics.push_problematic_address(metrics_category, address)
            return match
        else:
            self.log.warning(
                f"Analysis NOT done for {address} due to REST API problems")
            return False

    def compare_balances(self, address: str,
                         tx_svc_a: TransactionAPIinterface, tx_svc_b: TransactionAPIinterface,
                         metrics_category: str) -> bool:
        self.log.debug(f"\n***Compare balances for address: {address}")
        res_a = tx_svc_a.get_balances_for_safe(address)
        res_b = tx_svc_b.get_balances_for_safe(address)
        return self._compare_balances_payloads(address, res_a, res_b, metrics_category)

    def _compare_balances_in_usd_payloads(self, address: str, res_a, res_b,
                                          safe_metrics_category: str,
                                          token_address_metrics_category: str,
                                          field: str = "fiat_value") -> bool:
        if res_a and res_b:
            self.metrics.increment_counter(safe_metrics_category)
            token_map_a = self._generate_token_map(res_a, field)
            token_map_b = self._generate_token_map(res_b, field)

            match = True
            for token in res_a:
                self.metrics.increment_counter(token_address_metrics_category)
                token_addr = token["tokenAddress"] or "1"  # in case is Ether
                self.log.debug(
                    f"\n{field} for token address {token_addr} in domain a: {token_map_a.get(token_addr)} and in "
                    f"domain b {token_map_b.get(token_addr)}")

                value_a = token_map_a.get(token_addr)
                value_b = token_map_b.get(token_addr)
                if value_a is not None and value_b is not None:
                    value_a = float(value_a)
                    value_b = float(value_b)

                threshold = self.balance_in_usd_percentage_threshold

                if value_a == value_b:
                    self.log.debug(
                        f"{field} for token address {token_addr} is OK")
                    self.metrics.increment_match(
                        token_address_metrics_category)
                elif type(value_a) == float and type(value_b) == float and \
                        value_b > 0 and abs((value_b - value_a) / value_b) < threshold:
                    self.log.debug(f"{field} for token address {token_addr} do not exactly match "
                                   f"but delta is less than {threshold} so is OK")
                    self.metrics.increment_match(
                        token_address_metrics_category)
                else:
                    self.log.warning(
                        f"{field} for token address {token_addr} does NOT match")
                    match = False
            self.metrics.increment_match(safe_metrics_category) if match \
                else self.metrics.push_problematic_address(safe_metrics_category, address)
            return match
        else:
            self.log.warning(
                f"Analysis for field {field} NOT done for {address} due to REST API problems")
            return False

    def compare_balances_in_usd(self, address: str,
                                tx_svc_a: TransactionAPIinterface, tx_svc_b: TransactionAPIinterface,
                                safe_metrics_category: str,
                                token_addresses_metrics_category: str) -> bool:
        self.log.debug(f"\n***Compare balances in USD for address: {address}")
        res_a = tx_svc_a.get_balances_in_usd_for_safe(address)
        res_b = tx_svc_b.get_balances_in_usd_for_safe(address)
        return self._compare_balances_in_usd_payloads(address, res_a, res_b,
                                                      safe_metrics_category, token_addresses_metrics_category,
                                                      "fiatBalance")
