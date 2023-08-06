import logging, os
from dotenv import load_dotenv
from comparer import Comparer
from addresses_map import AddressesMap

load_dotenv()  # Load environment variables from .env file]\
def main():

    balance_in_usd_percentage_threshold = float(os.getenv('BALANCE_IN_USD_PERCENTAGE_THRESHOLD'))
    log_level = os.getenv('LOG_LEVEL')

    logging.basicConfig(level=log_level)
    map1 = AddressesMap('feed/infra/prod.json')
    comp = Comparer(domain_a=map1.get_domain_a(), domain_b=map1.get_domain_b(), log=logging,
                    balance_in_usd_percentage_threshold=balance_in_usd_percentage_threshold)
    comp.compare_safes(map=map1.get_full_dict())

    map2 = AddressesMap('feed/infra/test.json')
    comp = Comparer(domain_a=map2.get_domain_a(), domain_b=map2.get_domain_b(), log=logging,
                    balance_in_usd_percentage_threshold=balance_in_usd_percentage_threshold)
    comp.compare_safes(map=map2.get_full_dict())

    # map1 = AddressesMap('feed/infra/dev.json')
    # comp = Comparer(domain_a=map1.get_domain_a(), domain_b=map1.get_domain_b(), log=logging)
    # comp.compare_safes(map=map1.get_full_dict())
    # map4 = AddressesMap('feed/orgs/cowswap.json')
    # comp = Comparer(domain_a=map4.get_domain_a(), domain_b=map4.get_domain_b(), log=logging)
    # comp.compare_safes(map=map4.get_full_dict())


if __name__ == '__main__':
    main()
