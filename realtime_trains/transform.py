'''Transforms and cleans data from RealTime Trains API'''

import logging
from dotenv import load_dotenv
from extract import get_realtime_trains_data, save_data_to_file

LOCATION_REMOVE_KEYS = [
    'tiploc',
    'country',
    'system'
]
SERVICE_REMOVE_KEYS = [
    "trainIdentity",
    "runningIdentity",
    "isPassenger"
]
SERVICE_LOC_DETAILS_REMOVE_KEYS = [
    'realtimeActivated',
    'origin',
    'destination',
    'isCall',
    'isPublicCall',
    'realtimeArrivalNextDay',
    'realtimeDepartureNextDay',
    'platform',
    'platformConfirmed',
    'platformChanged'
]
SERVICE_CRITERIA = {
    "serviceType": "train"
}


def filter_keys(keys_to_remove: list, a_dict: dict) -> dict:
    '''Removes keys that can exist in a dictionary'''

    if not isinstance(a_dict, dict):
        raise TypeError(f"Expected dictionary item but got {type(a_dict)}")

    for key in keys_to_remove:
        a_dict.pop(key, None)

    return a_dict


def service_matches_criteria(service: dict, criteria: dict) -> bool:
    '''Checks if a service matches all criteria.'''
    for key, value in criteria.items():
        if service.get(key) != value:
            return False
    return True


def process_station(station: dict) -> dict:
    '''Processes a single station by removing specified keys and 
    filtering services based on multiple criteria.'''

    logging.info("Processing station: %s", station['location']['name'])

    station = filter_keys(["filter"], station)
    station["location"] = filter_keys(
        LOCATION_REMOVE_KEYS, station["location"])

    processed_services = []
    for service in station["services"]:
        if service_matches_criteria(service, SERVICE_CRITERIA):
            service = filter_keys(SERVICE_REMOVE_KEYS, service)
            service["locationDetail"] = filter_keys(
                SERVICE_LOC_DETAILS_REMOVE_KEYS, service["locationDetail"])
            processed_services.append(service)

    station["services"] = processed_services

    logging.info("Processing finished for station: %s",
                 station['location']['name'])

    return station


def process_all_stations(stations_data: list[dict]):
    '''Processes all station by filtering services and unnecessary keys'''
    logging.info("Transforming data...")
    for station in stations_data:
        station = process_station(station)
    logging.info("Transformation finished.")
    return stations_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    data = [get_realtime_trains_data("LDS")]
    modified_data = process_all_stations(data)
    save_data_to_file(modified_data, "modified_data_v1.json")
