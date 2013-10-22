import xml.etree.ElementTree as ET

import logging
logger = logging.getLogger("geniv3-decode")

namespaces = {'opennaas': 'http://example.com/opennaas'}


def get_opt_value(resource, key):
    try:
        return resource.find(key, namespaces=namespaces).text

    except Exception:
        return None


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


def decode_status_resources(xml_format):
    egress_ = []

    idx_ = 0
    root_ = ET.fromstring(xml_format)
    for resource_ in root_.findall('opennaas:resource', namespaces=namespaces):
        name_ = resource_.find('opennaas:name', namespaces=namespaces).text
        type_ = resource_.find('opennaas:type', namespaces=namespaces).text
        slice_ = resource_.find('opennaas:slice', namespaces=namespaces).text
        avail_ = resource_.find('opennaas:available', namespaces=namespaces).text
        end_ = resource_.find('opennaas:end', namespaces=namespaces).text
        client_ = resource_.find('opennaas:client', namespaces=namespaces).text
        client_mail_ = resource_.find('opennaas:client_mail', namespaces=namespaces).text
        client_id_ = resource_.find('opennaas:client_id', namespaces=namespaces).text
        to_ingress_ = get_opt_value(resource_, 'opennaas:to_ingress')
        to_egress_ = get_opt_value(resource_, 'opennaas:to_egress')

        egress_.append({'id': idx_,
                        'name': name_,
                        'type': type_,
                        'slice': slice_,
                        'available': avail_,
                        'end': end_,
                        'client': client_,
                        'client_mail': client_mail_,
                        'client_id': client_id_,
                        'ingress': to_ingress_,
                        'egress': to_egress_})
        idx_ += 1

    return egress_
