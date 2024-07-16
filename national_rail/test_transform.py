""" Unit tests to test transform functions """
import xml.etree.ElementTree as ET
from transform import (load_tree_root, reverse_tree, get_incidents, find_text_element, find_all_text_elements,
                       convert_html_to_text, convert_to_datetime, check_creation_within_last_5_minutes,
                       transform_xml_file, process_pt_incidents)

with open("test_data.xml", "r", encoding="utf-8") as file:
    data = file.read()

NS = {"ns": "http://nationalrail.co.uk/xml/incident",
      "com": "http://nationalrail.co.uk/xml/common"}


def test_transform_xml_file_good_input():
    """ Tests process pt incidents function returns a list
        if input is an xml file as a string. """

    result = transform_xml_file(data, NS)
    assert isinstance(result, list)


def test_process_pt_incidents_bad_input():
    """ Tests process pt incidents function returns empty list 
        if input is an empty string. """

    assert process_pt_incidents("", NS) == []


def test_load_tree_root():
    """ Tests a root is returned for an inputted tree. """

    root = load_tree_root(data)
    assert isinstance(root, ET.Element)


def test_get_incidents_finds_incidents():
    """ Tests get_incidents function finds 2 incidents for a root 
        with 2 incidents. """

    root = load_tree_root(data)
    incidents = get_incidents(root, NS)

    assert len(incidents) == 2


def test_get_incidents_finds_no_incidents():
    """ Tests get_incidents function finds 0 incidents for a new root 
        with no child nodes. """

    new_root = ET.Element("root")
    incidents = get_incidents(new_root, NS)

    assert len(incidents) == 0


def test_get_incidents_finds_incidents_for_reversed_tree():
    """ Tests get_incidents function finds 2 incidents for a root 
        with 2 incidents and its reversed tree. """

    root = load_tree_root(data)
    reversed_root = reverse_tree(root)

    incidents_not_reversed = get_incidents(root, NS)
    incidents_reversed = get_incidents(reversed_root, NS)

    assert len(incidents_not_reversed) == len(incidents_reversed)
    assert len(incidents_reversed) == 2


def test_convert_html_to_text():
    ...


# test timestamp

# later maybe test find text element - find incident number
