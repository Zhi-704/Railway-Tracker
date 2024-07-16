""" Module for transforming data received from the National Rail API into a 
    useful format. """

import logging

from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


def read_data_from_file(filename: str) -> str:
    """ Opens file, reads and returns its content as a String. """

    with open(filename, "r", encoding="utf-8") as file:
        f = file.read()
    return f


def load_tree_root(national_rail_xml: str) -> ET.Element:
    """ Returns root node of tree (from data.xml) """

    tree = ET.ElementTree(ET.fromstring(national_rail_xml))
    return tree.getroot()


def reverse_tree(root: ET.Element) -> ET.Element:
    """ Creates a new tree containing the root and its elements in reverse, to allow
        for traversing the tree in reverse. Returns the new tree by its root. """

    reversed_elements = list(reversed(list(root.iter())))
    new_root = ET.Element("root")

    for element in reversed_elements:
        new_root.append(element)

    return new_root


def get_incidents(root: str, namespaces: dict) -> ET.Element:
    """ Extracts each incident from the NationalRail data and returns it. """

    return root.findall('ns:PtIncident', namespaces)


def find_text_element(element: ET.Element, path: str, namespaces: str) -> str:
    """ Searches for element by path and namespace, returns text if element exists. """

    element_found = element.find(path, namespaces)
    return element_found.text if element_found is not None else None


def find_all_text_elements(element: ET.Element, path: str, namespaces: str) -> list[str]:
    """ Searches for all elements by path and namespace, returns list of elements
        as text if they exist. """

    elements_found = element.findall(path, namespaces)
    return [e.text for e in elements_found if e.text]


def convert_html_to_text(html_text: str) -> str:
    """ Extracts String from html text and returns it."""

    soup = BeautifulSoup(html_text, 'lxml')
    return soup.get_text(separator=' ', strip=True)


def convert_to_datetime(time: str) -> datetime:
    """ Converts string in datetime format into a datetime object and returns it. """

    return datetime.fromisoformat(time.replace('Z', ''))


def check_creation_within_last_5_minutes(creation_time: datetime) -> bool:
    """ Checks that the creation time of an incident occurred within the last 5 minutes. """

    current_time = datetime.now()
    time_diff = current_time - creation_time

    return time_diff <= timedelta(minutes=5)


def process_pt_incidents(incidents: list[ET.Element], namespaces: dict) -> list[dict]:
    """ Extracts relevant data for each incident reported. """
    dataset = []

    for incident in incidents:

        creation_time = convert_to_datetime(find_text_element(
            incident, 'ns:CreationTime', namespaces))

        if not check_creation_within_last_5_minutes(creation_time):
            # remove not to allow all incidents
            break

        incident_number = find_text_element(
            incident, 'ns:IncidentNumber', namespaces)

        operator_codes = find_all_text_elements(
            incident, "ns:Affects/ns:Operators/ns:AffectedOperator/ns:OperatorRef", namespaces)

        start_time = find_text_element(
            incident, 'ns:ValidityPeriod/com:StartTime', namespaces)
        end_time = find_text_element(
            incident, 'ns:ValidityPeriod/com:EndTime', namespaces)

        is_planned = find_text_element(incident, 'ns:Planned', namespaces)

        summary = find_text_element(incident, 'ns:Summary', namespaces)

        description = convert_html_to_text(find_text_element(
            incident, 'ns:Description', namespaces))

        uri = find_text_element(
            incident, "ns:InfoLinks/ns:InfoLink/ns:Uri", namespaces).replace('/n', " ").strip()

        routes_affected = convert_html_to_text(find_text_element(
            incident, "ns:Affects/ns:RoutesAffected", namespaces))

        data = {
            'incident_number': incident_number,
            'operator_codes': operator_codes,  # list
            'creation_time': creation_time,
            'start_time': start_time,
            'end_time': end_time,
            'is_planned': is_planned,
            'summary': summary,
            'description': description,
            'uri': uri,
            'routes_affected': routes_affected
        }
        dataset.append(data)

    return dataset


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    logging.info("Transformation of NationalRail has began")

    nr_namespaces = {'ns': 'http://nationalrail.co.uk/xml/incident',
                     'com': 'http://nationalrail.co.uk/xml/common'}

    national_rail_data = read_data_from_file("data.xml")

    national_rail_tree_root = reverse_tree(load_tree_root(national_rail_data))

    all_incidents = get_incidents(national_rail_tree_root, nr_namespaces)

    incidents_dataset = process_pt_incidents(all_incidents, nr_namespaces)

    logging.info("Transformation of NationalRail completed successfully")
