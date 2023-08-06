from xml.dom import minidom


def read_conf(xml_file, xml_content=None):
    if xml_file is not None:
        doc = minidom.parse(xml_file)
    elif xml_content is not None:
        doc = minidom.parseString(xml_content)
    root = doc.documentElement
    conf_list = []
    for node in root.getElementsByTagName("property"):
        name = node.getElementsByTagName("name")[0].firstChild.data
        value_elem = node.getElementsByTagName("value")[0].firstChild
        value = value_elem.data if value_elem is not None else ''
        resource_elem = node.getElementsByTagName("source")
        resource = resource_elem[0].firstChild.data if resource_elem else ''
        conf_list.append({'key': name, 'value': value, 'resource': resource})
    return conf_list


def read_conf_2_dict(xml_file, xml_content=None):
    conf_list = read_conf(xml_file, xml_content)
    conf_dict = {}
    for conf_item in conf_list:
        conf_dict[conf_item['key']] = conf_item['value']
    return conf_dict
