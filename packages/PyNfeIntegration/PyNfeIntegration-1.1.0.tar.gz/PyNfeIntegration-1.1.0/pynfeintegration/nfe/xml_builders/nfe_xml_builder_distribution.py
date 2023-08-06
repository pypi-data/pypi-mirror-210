from .nfe_xml_builder_base import NfeXmlBuilderBase
from lxml import etree
from pynfeintegration.constantes.name_spaces import METHOD_NAMESPACE, NFE_NAMESPACE
from pynfeintegration.constantes.codes import UF_CODES


class NfeXmlBuilderDistribution(NfeXmlBuilderBase):
    @staticmethod
    def build_header(method: str, data: etree):
        root, body = NfeXmlBuilderBase.build_header()
        x = etree.SubElement(body, 'nfeDistDFeInteresse', xmlns=METHOD_NAMESPACE + method)
        a = etree.SubElement(x, 'nfeDadosMsg')

        a.append(data)
        return root

    def build(self):
        raiz = etree.Element('distDFeInt', versao='1.01', xmlns=NFE_NAMESPACE)
        etree.SubElement(raiz, 'tpAmb').text = str(self._sefaz_env)
        if self.uf:
            etree.SubElement(raiz, 'cUFAutor').text = UF_CODES[self.uf]
        if self.cnpj:
            etree.SubElement(raiz, 'CNPJ').text = self.cnpj
        else:
            etree.SubElement(raiz, 'CPF').text = self.cpf

        if not self.chave and not self.consulta_nsu_especifico:
            distNSU = etree.SubElement(raiz, 'distNSU')
            etree.SubElement(distNSU, 'ultNSU').text = str(self.nsu).zfill(15)
        if self.chave:
            consChNFe = etree.SubElement(raiz, 'consChNFe')
            etree.SubElement(consChNFe, 'chNFe').text = self.chave
        if self.consulta_nsu_especifico:
            consNSU = etree.SubElement(raiz, 'consNSU')
            etree.SubElement(consNSU, 'NSU').text = str(self.nsu).zfill(15)

        root = NfeXmlBuilderDistribution.build_header('NFeDistribuicaoDFe', raiz)

        return NfeXmlBuilderDistribution.parse_to_str(root)
