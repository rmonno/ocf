import xml.etree.ElementTree as ET

import logging
logger = logging.getLogger("geniv3-encode")

namespaces = {'opennaas': 'http://example.com/opennaas'}


def encode_allocate_resource(ingress):
    root_ = ET.Element('rspec', {'type': 'request',
                                 'xmlns:opennaas': 'http://example.com/opennaas'})

    egress_ = ET.SubElement(root_, 'opennaas:resource')
    ET.SubElement(egress_,'opennaas:name').text = ingress.get('name')
    ET.SubElement(egress_,'opennaas:type').text = ingress.get('type')

    inner_ = ET.SubElement(egress_,'opennaas:roadm')
    ET.SubElement(inner_,'opennaas:in_endpoint').text = ingress.get('in_ep')
    ET.SubElement(inner_,'opennaas:in_label').text = ingress.get('in_lab')
    ET.SubElement(inner_,'opennaas:out_endpoint').text = ingress.get('out_ep')
    ET.SubElement(inner_,'opennaas:out_label').text = ingress.get('out_lab')

    return ET.tostring(root_)
