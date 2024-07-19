""" Unit tests to test transform functions. """
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import unittest

from transform import (
    load_tree_root,
    reverse_tree,
    get_incidents,
    find_text_element,
    find_all_text_elements,
    convert_html_to_text,
    convert_to_datetime,
    check_creation_within_last_5_minutes,
    transform_xml_file,
    process_pt_incidents)


class TransformationTests(unittest.TestCase):
    """ Class for testing functions from the transform.py file. """

    def setUp(self):

        with open("national_rail/test_data.xml", "r", encoding="utf-8") as file:
            self.data = file.read()

        self.namespace = {
            "ns": "http://nationalrail.co.uk/xml/incident",
            "com": "http://nationalrail.co.uk/xml/common"
        }

        self.root = load_tree_root(self.data)

    def test_transform_xml_file_good_input(self):
        """ Tests process pt incidents function returns a list
            if input is an xml file as a string. """

        result = transform_xml_file(self.data, self.namespace)
        assert isinstance(result, list)

    def test_process_pt_incidents_bad_input(self):
        """ Tests process pt incidents function returns empty list 
            if input is an empty string. """

        self.assertEqual(process_pt_incidents("", self.namespace), [])

    def test_load_tree_root(self):
        """ Tests a root is returned for an inputted tree. """

        assert isinstance(self.root, ET.Element)

    def test_get_incidents_finds_incidents(self):
        """ Tests get_incidents function finds 2 incidents for a root 
            with 2 incidents. """

        incidents = get_incidents(self.root, self.namespace)

        assert len(incidents) == 2

    def test_get_incidents_finds_no_incidents(self):
        """ Tests get_incidents function finds 0 incidents for a new root
            with no child nodes. """

        new_root = ET.Element("root")
        incidents = get_incidents(new_root, self.namespace)

        assert len(incidents) == 0

    def test_get_incidents_finds_incidents_for_reversed_tree(self):
        """ Tests get_incidents function finds 2 incidents for a root
            with 2 incidents and its reversed tree. """

        reversed_root = reverse_tree(self.root)
        incidents_not_reversed = get_incidents(self.root, self.namespace)
        incidents_reversed = get_incidents(reversed_root, self.namespace)

        self.assertEqual(len(incidents_not_reversed), len(incidents_reversed))
        assert len(incidents_reversed) == 2

    def test_convert_html_to_text(self):
        """ Tests that HTML text is converted to String correctly. """

        html = "<div><p>Hello, <b>world</b>!</p><p>Goodbye, <i>world</i>!</p></div>"
        expected = "Hello, world ! Goodbye, world !"
        assert convert_html_to_text(html) == expected

    def test_empty_html_to_text(self):
        """ Tests that an empty HTML returns an empty String. """

        html = ""
        expected = ""
        assert convert_html_to_text(html) == expected

    def test_html_to_text_with_comments(self):
        """ Tests that a HTML with comments returns a String without the comments. """

        html = "<!-- This is a comment --><p>Hello, world!</p>"
        expected = "Hello, world!"
        assert convert_html_to_text(html) == expected

    def test_convert_to_datetime_with_z(self):
        """ Tests that date time as a String is converted into a datetime object.
            Space replaces T, Z replaced with empty string. """

        time_str = "2024-07-16T19:22:56Z"
        expected = datetime(2024, 7, 16, 19, 22, 56)
        assert convert_to_datetime(time_str) == expected

    def test_convert_to_datetime_without_z(self):
        """ Tests that date time as a String is converted into a datetime object.
            Z replaced with empty string. """

        time_str = "2024-07-16T19:22:56"
        expected = datetime(2024, 7, 16, 19, 22, 56)
        assert convert_to_datetime(time_str) == expected

    def test_convert_to_datetime_invalid_format(self):
        """ Tests that converting an invalid format to datetime raises a ValueError. """

        time_str = "16/07/2024 12:34:56"
        with self.assertRaises(ValueError):
            convert_to_datetime(time_str)

    def test_convert_to_datetime_empty_string(self):
        """ Tests that converting an empty string to datetime raises a ValueError. """

        time_str = ""
        with self.assertRaises(ValueError):
            convert_to_datetime(time_str)

    def test_within_5_minutes_returns_true(self):
        """ Tests that creation time is within 5 minutes returns True. """

        creation_time = datetime.now() - timedelta(minutes=4)
        self.assertTrue(check_creation_within_last_5_minutes(creation_time))

    def test_within_5_minutes_returns_false(self):
        """ Tests that creation time is within 5 minutes returns False. """

        creation_time = datetime.now() - timedelta(minutes=6)
        self.assertFalse(check_creation_within_last_5_minutes(creation_time))

    def test_find_incidents_element_with_namespace(self):
        """ Tests that IncidentNumber element is found within an incident element. """

        path = "ns:IncidentNumber"
        element = get_incidents(self.root, self.namespace)[0]
        self.assertEqual(find_text_element(
            element, path, self.namespace), "randomIncidentNumber1")

    def test_find_element_with_namespace_returns_none(self):
        """ Tests that no element is found for element that doesn't exist. """

        path = "ns:blah"
        element = get_incidents(self.root, self.namespace)[0]
        self.assertEqual(find_text_element(
            element, path, self.namespace), None)

    def test_find_element_with_namespace_invalid_namespace(self):
        """ Tests that no element is found within an invalid namespace. """

        path = "empty_namespace"
        element = get_incidents(self.root, self.namespace)[0]
        self.assertEqual(find_text_element(
            element, path, self.namespace), None)

    def test_find_all_text_operator_elements(self):
        """ Tests that all OperatorRef elements are found within an Incident element. """

        path = "ns:Affects/ns:Operators/ns:AffectedOperator/ns:OperatorRef"
        element = get_incidents(self.root, self.namespace)[1]
        self.assertEqual(len(find_all_text_elements(
            element, path, self.namespace)), 2)
        self.assertEqual(find_all_text_elements(
            element, path, self.namespace), ['XC', 'GW'])
