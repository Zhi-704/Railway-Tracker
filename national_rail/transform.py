"""Module for transforming data received from the National Rail API into a 
    useful format."""

from os import environ as ENV
import logging

from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# from extract import


def read_data_from_file(filename: str) -> str:
    """ Opens file, reads and returns its content as a String. """
    with open(filename, "r", encoding="utf-8") as file:
        f = file.read()
    return f


def load_tree_root(national_rail_xml: str) -> ET.Element:
    """ Returns root node of tree (from data.xml) """

    tree = ET.ElementTree(ET.fromstring(national_rail_xml))
    return tree.getroot()


def get_incidents(root: str) -> ET.Element:
    """ Extracts each incident from the NationalRail data and returns it. """

    namespace = {'ns': 'http://nationalrail.co.uk/xml/incident',
                 'com': 'http://nationalrail.co.uk/xml/common'}

    incidents = root.findall('ns:PtIncident', namespace)

    return incidents


# def process_pt_incidents(incidents: list[ET.Element]):
#     """ Extracts relevant data for each incident reported. """
#     dataset = []

#     for incident in incidents:
#         incident_ns = {'ns': 'http://nationalrail.co.uk/xml/incident'}
#         common_ns = {'com': 'http://nationalrail.co.uk/xml/common'}

#         # incident number
#         incident_number = get_text(incident, 'ns:IncidentNumber', incident_ns)
#         print(incident_number)

#         # operator code

#         # disruption info

#         # creation time
#         creation_time = get_text(incident, 'ns:CreationTime', incident_ns)

#         # difffff:
#         validity_period = incident.find('ns:ValidityPeriod', incident_ns)

#         # incident start
#         start_time = get_text(validity_period, 'com:StartTime', common_ns)
#         # incident end
#         end_time = get_text(validity_period, 'com:EndTime', common_ns)

#         # is planned

#         # incident summary
#         summary = get_text(incident, 'ns:Summary', incident_ns)

#         # incident description
#         description = get_text(incident, 'ns:Description', incident_ns)

#         # incident uri

#         # affected routes


def get_text(element: ET.Element, path: str, namespace: str):

    sub_element = element.find(path, {"ns": namespace})

    if sub_element is not None:
        return sub_element.text
    else:
        logging.error("Failed to retrieve data.")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    national_rail_data = read_data_from_file("test_data.xml")

    national_rail_tree_root = load_tree_root(national_rail_data)

    incidents = get_incidents(national_rail_tree_root)

    process_pt_incidents(incidents)

    # print(len(incidents))
