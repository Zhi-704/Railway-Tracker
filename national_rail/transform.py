"""Module for transforming data received from the National Rail API into a 
    useful format."""

from os import environ as ENV
import logging

from dotenv import load_dotenv
import xml.etree.ElementTree as ET


def read_data_from_file(filename: str) -> str:
    """ Opens file, reads and returns its content as a String. """
    with open(filename, "r", encoding="utf-8") as file:
        f = file.read()
    return f


def load_tree_root(national_rail_xml: str) -> ET.Element:
    """ Returns root node of tree (from data.xml) """

    tree = ET.ElementTree(ET.fromstring(national_rail_xml))
    return tree.getroot()


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


def process_pt_incidents(incidents: list[ET.Element], namespaces: dict) -> list[dict]:
    """ Extracts relevant data for each incident reported. """
    dataset = []

    for incident in incidents:
        incident_number = find_text_element(
            incident, 'ns:IncidentNumber', namespaces)

        # operator code:  many to many?
        operator_codes = find_all_text_elements(
            incident, "ns:Affects/ns:Operators/ns:AffectedOperator/ns:OperatorRef", namespaces)

        # disruption info --- REMOVE!

        creation_time = find_text_element(
            incident, 'ns:CreationTime', namespaces)

        start_time = find_text_element(
            incident, 'ns:ValidityPeriod/com:StartTime', namespaces)
        end_time = find_text_element(
            incident, 'ns:ValidityPeriod/com:EndTime', namespaces)

        is_planned = find_text_element(incident, 'ns:Planned', namespaces)

        summary = find_text_element(incident, 'ns:Summary', namespaces)

        description = find_text_element(
            incident, 'ns:Description', namespaces)  # html

        uri = find_text_element(
            incident, "ns:InfoLinks/ns:InfoLink/ns:Uri", namespaces).replace('/n', " ").strip()

        routes_affected = find_text_element(
            incident, "ns:Affects/ns:RoutesAffected", namespaces)  # html

        data = {
            'incident_number': incident_number,
            'operator_codes': operator_codes,
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

        print(incident_number)
        print(operator_codes)
        print(creation_time)
        print(start_time, end_time)
        print(is_planned)
        print(summary)
        print(uri)
        print(routes_affected)

        print("\n")

    return dataset


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    namespaces = {'ns': 'http://nationalrail.co.uk/xml/incident',
                  'com': 'http://nationalrail.co.uk/xml/common'}

    national_rail_data = read_data_from_file("test_data.xml")

    national_rail_tree_root = load_tree_root(national_rail_data)

    incidents = get_incidents(national_rail_tree_root, namespaces)

    process_pt_incidents(incidents, namespaces)

    # print(len(incidents))
