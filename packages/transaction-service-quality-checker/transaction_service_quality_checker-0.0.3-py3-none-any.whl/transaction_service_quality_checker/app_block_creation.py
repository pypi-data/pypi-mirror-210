import logging
from dotenv import load_dotenv
from block_creation import BlockCreation
from addresses_map import AddressesMap

load_dotenv()  # Load environment variables from .env file]
api_key = "PPRYT4T8B447KFFXQYRQ7JI3FK78RZT81Y"

def main():
    logging.basicConfig(level=logging.INFO)
    map1 = AddressesMap('feed/infra/compared/output_metrics_5000_0_1000.json')
    creation = BlockCreation(api_key, log=logging)
    creation.get_safes_creation_block(map=map1.get_full_dict())


if __name__ == '__main__':
    main()
