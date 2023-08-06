from abc import ABC, abstractmethod
from lxml import etree
from pynfeintegration.constantes.name_spaces import SOAP_NAMESPACE, XSD_NAMESPACE, XSI_NAMESPACE
from pynfeintegration.base.classes.base_entity import BaseEntity
import re


class NfeXmlBuilderBase(ABC, BaseEntity):
    @abstractmethod
    def build(self):
        pass

    @staticmethod
    def build_header():
        # Monta o XML SOAP que sera enviado na requisicao
        root = etree.Element('{%s}Envelope' % SOAP_NAMESPACE, nsmap={
            'xsi': XSI_NAMESPACE, 'xsd': XSD_NAMESPACE, 'soap': SOAP_NAMESPACE})
        body = etree.SubElement(root, '{%s}Body' % SOAP_NAMESPACE)

        return root, body

    @staticmethod
    def parse_to_str(xml) -> str:
        xml_prefix = '<?xml version="1.0" encoding="UTF-8"?>'

        # limpa xml com caracteres bugados para infNFeSupl em NFC-e
        xml = re.sub(
            '<qrCode>(.*?)</qrCode>',
            lambda x: x.group(0).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', ''),
            etree.tostring(xml, encoding='unicode').replace('\n', '')
        )
        return xml_prefix + xml
