import json


class AddressesMap:
    def __init__(self, path_to_json: str):
        self.path_to_json = path_to_json
        f = open(self.path_to_json)
        self.data = json.load(f)
        f.close()

    def get_full_dict(self) -> dict:
        return self.data

    def get_domains(self):
        return self.data.get("config_domains")

    def get_domain_a(self):
        return self.data.get("config_domains").get("a")

    def get_domain_b(self):
        return self.data.get("config_domains").get("b")
