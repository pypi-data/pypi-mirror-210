import logging

class Metrics:
    def __init__(self, log: logging.Logger = logging):
        self.metrics = {}
        self.log = log

    def check_valid_category(self, category: str) -> bool:

        if self.metrics.get(category) is None:
            raise ValueError('Category is not defined')

    def create_category(self, category: str):
        self.metrics[category] = {
            "counter": 0,
            "match": 0,
            "problematic_addresses": []
        }

    def check_valid_subcategory(self, category: str, subcategory: str) -> bool:
        return self.metrics.get(category) is not None and \
               self.metrics.get(category).get(subcategory) is not None

    def set_subcategory(self, category: str, subcategory: str, value):
        self.metrics[category][subcategory] = value

    def get_subcategory(self, category: str, subcategory: str):
        return self.metrics[category][subcategory]

    def increment_counter(self, category: str):
        self.check_valid_category(category)
        self.metrics[category]["counter"] += 1

    def get_counter(self, category: str):
        self.check_valid_category(category)
        return self.metrics[category]["counter"]

    def increment_match(self, category: str):
        self.check_valid_category(category)
        self.metrics[category]["match"] += 1

    def get_match(self, category: str):
        self.check_valid_category(category)
        return self.metrics[category]["match"]

    def push_problematic_address(self, category: str, address: str):
        self.check_valid_category(category)
        if not isinstance(address, str):
            self.log.warning(f"Address {address} is not str")
            return
        self.metrics[category]["problematic_addresses"].append(address)

    def get_problematic_addresses(self, category: str):
        self.check_valid_category(category)
        return self.metrics[category]["problematic_addresses"]