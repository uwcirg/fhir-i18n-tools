#!/usr/bin/env python3

import json
import os
import sys

from lxml import etree as ET


namespaces = {'fhir': 'http://hl7.org/fhir'}


def parse_fhir_xml(xml_string):
    """Extract and return strings from elements marked with translatable FHIR extension"""
    # LXML infers encoding from XML metadata
    root = ET.fromstring(xml_string.encode('utf-8'))

    translatable_extension_url = 'http://hl7.org/fhir/StructureDefinition/elementdefinition-translatable'
    # todo: separate finding/extract into separate steps
    translatable_strings = root.xpath(
        #'//fhir:extension[@url="%s"]' % translatable_extension_url,
        '//fhir:extension[@url="%s"]/../@value' % translatable_extension_url,
        namespaces=namespaces
    )
    return translatable_strings


def format_arb(strings):
    """Create ARB file keyed on source language present in FHIR"""
    arb_key_value = dict(zip(strings, strings))

    dump = json.dumps(
        obj=arb_key_value,
        indent=2,
        separators=(',', ': '),
        sort_keys=True,
    )
    return dump


if __name__ == '__main__':
    # output file is first arg
    arb_filename = sys.argv[1]

    strings = []
    for filename in sys.argv[2:]:
        print('processing: ', filename)
        with open(filename, 'r') as xml_file:
            xml_string = xml_file.read()
        strings.extend(parse_fhir_xml(xml_string))

    arb_content = format_arb(strings)
    with open(arb_filename , 'w') as arb_file:
        arb_file.write(arb_content)
    print('created: ', arb_filename)
