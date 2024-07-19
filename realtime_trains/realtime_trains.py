import logging
from dotenv import load_dotenv

from extract import get_api_data_of_all_stations
from transform import process_all_stations
from load import import_to_database

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    data = get_api_data_of_all_stations()
    modified_data = process_all_stations(data)
    print("\n-------------------------")
    import_to_database(modified_data)
