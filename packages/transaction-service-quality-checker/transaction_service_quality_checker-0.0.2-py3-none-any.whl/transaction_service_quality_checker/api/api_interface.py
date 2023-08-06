import requests


class APIInteface:
    def __init__(self, domain: str, name: str, version: str = 'v1'):
        self.domain = domain
        self.name = name
        self.version = version
        self.base_url = f"{domain}/api/{version}"

    def is_healthy(self, health_check_path: str = 'about'):
        url = f"{self.base_url}/{health_check_path}"
        res = requests.get(url)
        return res.status_code == 200
