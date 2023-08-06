from .nfe_xml_builder_base import NfeXmlBuilderBase
from lxml import etree
from pynfeintegration.constantes.name_spaces import METHOD_NAMESPACE, NFE_NAMESPACE
from pynfeintegration.constantes.codes import UF_CODES
from pynfeintegration.constantes.versions import DEFAULT_VERSION


class NfeXmlBuilderStatus(NfeXmlBuilderBase):
    @staticmethod
    def build_header(method: str, data: etree):
        root, body = NfeXmlBuilderBase.build_header()
        a = etree.SubElement(body, 'nfeDadosMsg', xmlns=METHOD_NAMESPACE + method)
        a.append(data)

        return root

    def build(self):
        root = etree.Element('consStatServ', versao=DEFAULT_VERSION, xmlns=NFE_NAMESPACE)
        etree.SubElement(root, 'tpAmb').text = str(self._sefaz_env)
        etree.SubElement(root, 'cUF').text = UF_CODES[self.uf]
        etree.SubElement(root, 'xServ').text = 'STATUS'

        root = NfeXmlBuilderStatus.build_header('NFeStatusServico4', root)

        return NfeXmlBuilderStatus.parse_to_str(root)
