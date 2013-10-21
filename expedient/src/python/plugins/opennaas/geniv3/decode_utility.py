import xml.etree.ElementTree as ET

import logging
logger = logging.getLogger("geniv3-decode")

namespaces = {'opennaas': 'http://example.com/opennaas'}


def decode_list_resources(xml_format):
    egress_ = []

    root_ = ET.fromstring(xml_format)
    for resource_ in root_.findall('opennaas:resource', namespaces=namespaces):
        name_ = resource_.find('opennaas:name', namespaces=namespaces).text
        type_ = resource_.find('opennaas:type', namespaces=namespaces).text
        endpoint_ = resource_.find('opennaas:endpoint', namespaces=namespaces).text
        label_ = resource_.find('opennaas:label', namespaces=namespaces).text
        avail_ = resource_.find('opennaas:available', namespaces=namespaces).text

        egress_.append({'name': name_,
                        'type': type_,
                        'endpoint': endpoint_,
                        'label': label_,
                        'available': avail_})

    return egress_
