import logging
from dotenv import load_dotenv
from extract import get_realtime_trains_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    data = get_realtime_trains_data("LDS", "data.json")
