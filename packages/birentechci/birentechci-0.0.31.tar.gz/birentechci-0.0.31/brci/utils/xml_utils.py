from typing import Dict
from xml.dom.minidom import parseString

import dicttoxml
import xmltodict


def load_xml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        xmlData = f.read()
    return xmltodict.parse(xmlData)


def write_xml(path: str, data: Dict):
    xmlData = dicttoxml.dicttoxml(data).decode("utf-8")
    if path:
        with open(path, "w", encoding="utf-8") as wF:
            dom = parseString(xmlData)
            xmlPretty = dom.toprettyxml()
            wF.write(xmlPretty)
    return xmlData
