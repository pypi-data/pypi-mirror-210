# -*- coding: utf-8 -*-
from pynfeintegration.constantes import DEFAULT_VERSION, CONTINGENCY_SVAN, CONTINGENCY_SVRS
from pynfeintegration.webservices import WEB_SERVICE_MODEL
import requests
from pynfeintegration.certificates import PfxCertificate
from pynfeintegration.base import BaseRequester
from .xml_builders import NfeXmlBuilder


class NFeRequester(BaseRequester):
    _version = DEFAULT_VERSION

    def consult_invoices(self, cnpj=None, cpf=None, chave=None, nsu=0, consulta_nsu_especifico=False):
        """
        O XML do pedido de distribuição suporta três tipos de consultas
        que são definidas de acordo com a tag informada no XML.

        As tags são distNSU, consNSU e consChNFe:
        a) distNSU – Distribuição de Conjunto de DF-e a Partir do NSU Informado
        b) consNSU – Consulta DF-e Vinculado ao NSU Informado
        c) consChNFe – Consulta de NF-e por Chave de Acesso Informada

        :param cnpj: CNPJ do interessado
        :param cpf: CPF do interessado
        :param chave: Chave da NF-e a ser consultada
        :param nsu: Ultimo nsu ou nsu específico para ser consultado
        :param consulta_nsu_especifico:
            True para consulta por nsu específico
            False para consulta por nsu último
        :return: xml do resultado da consulta

        Exemplos de usos:
        * consChNFe: consulta_distribuicao(cnpj=CNPJ, chave=CHAVE)
        * distNSU: consulta_distribuicao(cnpj=CNPJ)
        * consNSU: consulta_distribuicao(cnpj=CNPJ, nsu=10, consulta_nsu_especifico=True)

        """

        # url
        url = self._get_url_an(url_type='DISTRIBUICAO')
        xml = NfeXmlBuilder.build('DISTRIBUICAO', _sefaz_env=self._sefaz_env, uf=self.uf, cnpj=cnpj, cpf=cpf,
                                  chave=chave, nsu=nsu, consulta_nsu_especifico=consulta_nsu_especifico)
        return self._post(url, xml)

    def service_status(self, model):
        """
        Verifica status do servidor da receita.
        :param model: model é a string com tipo de serviço que deseja consultar, Ex: nfe ou nfce
        """
        url = self._get_url(model, 'STATUS')

        xml = NfeXmlBuilder.build('STATUS', _sefaz_env=self._sefaz_env, uf=self.uf)

        return self._post(url, xml)

    def _get_url_an(self, url_type: str):
        if self._is_production:
            prefix = 'https://www1.' if url_type == 'DISTRIBUICAO' else 'https://www.'
        else:
            prefix = 'https://hom1.'

        self.url = prefix + WEB_SERVICE_MODEL['NFE']['AN'][url_type]
        return self.url

    def _get_contingency_url(self, web_model: dict, model: str, url_type: str):
        if (self.uf in CONTINGENCY_SVAN) and model == 'nfe':
            self.url = web_model['SVAN'][self._env] + web_model['SVAN'][url_type]
        elif (self.uf in CONTINGENCY_SVRS) or (self.uf in CONTINGENCY_SVAN):
            self.url = web_model['SVRS'][self._env] + web_model['SVRS'][url_type]

        return self.url

    def _get_own_url_from_uf(self, web_model: dict, model: str, url_type: str):
        # CE é a única UF que possuem NFE SVRS e NFCe próprio
        # PE e BA são as únicas UF'sque possuem NFE proprio e SVRS para NFCe

        if (model == 'nfe' and self.uf == 'CE') or (model == 'nfce' and (self.uf in  ['PE', 'BA'])):
            self.url = web_model['SVRS'][self._env] + web_model['SVRS'][url_type]
        else:
            self.url = web_model[self.uf][self._env] + web_model[self.uf][url_type]

        return self.url

    def _get_url_for_uf_without_webservice(self, web_model: dict, model: str, url_type: str):
        uf_without_ws = ['AC', 'AL', 'AP', 'DF', 'ES', 'PB', 'PI', 'RJ', 'RN', 'RO', 'RR', 'SC', 'SE', 'TO', 'PA']
        if (self.uf in uf_without_ws) or (self.uf == 'MA' and model == 'nfce'):
            self.url = web_model['SVRS'][self._env] + web_model['SVRS'][url_type]
        # unico UF que utiliza SVAN ainda para NF-e
        # SVRS para NFC-e
        elif self.uf == 'MA' and model == 'nfe':
            self.url = web_model['SVAN'][self._env] + web_model['SVAN'][url_type]
        else:
            raise Exception(f"Url não encontrada para {model} e {url_type} {self.uf.upper()}")

        return self.url

    def _get_url(self, model: str, url_type: str, contingency=False):

        web_model = WEB_SERVICE_MODEL[model.upper()]
        if not web_model:
            raise Exception('Modelo não encontrado! Defina model="nfe" ou "nfce"')

        """ Retorna a url para comunicação com o webservice """
        if contingency:
            return self._get_contingency_url(model, url_type)

        # estado que implementam webservices proprios
        uf_with_own_url = ['PR', 'MS', 'SP', 'AM', 'CE', 'BA', 'GO', 'MG', 'MT', 'PE', 'RS']
        if self.uf in uf_with_own_url:
            return self._get_own_url_from_uf(web_model, model, url_type)

        # Estados que utilizam outros ambientes
        return self._get_url_for_uf_without_webservice(web_model, model, url_type)

    def _post_header(self):
        """Retorna um dicionário com os atributos para o cabeçalho da requisição HTTP"""

        response = {
            'content-type': 'application/soap+xml; charset=utf-8;',
            'Accept': 'application/soap+xml; charset=utf-8;',
        }
        # PE exige SOAPAction no header
        if self.uf == 'PE':
            response["SOAPAction"] = ""
        return response

    def _post(self, url, xml):
        certificate_parser_a1 = PfxCertificate(self.certificate, self.certificate_password)
        certificate_key, certificate = certificate_parser_a1.parse_to_pem()
        temp_files_path = (certificate, certificate_key)
        try:
            result = requests.post(url, xml, headers=self._post_header(), cert=temp_files_path, verify=False)
            result.encoding = 'utf-8'
            return result
        except requests.exceptions.RequestException as e:
            raise e
        finally:
            certificate_parser_a1.clear_temp_files()
