# -*- coding: utf-8 -*-

from pynfeintegration.base import BaseEntity
from OpenSSL import crypto
import tempfile
import os


class BaseCertificate(BaseEntity):
    """Classe abstrata responsavel por definir o modelo padrao para as demais
    classes de certificados digitais.

    Caso va implementar um novo formato de certificado, crie uma classe que
    herde desta."""

    def __new__(cls, *args, **kwargs):
        if cls == BaseCertificate:
            raise Exception('Atenção! Não instancie esta classe diretamente, ela deve ser herdada!')
        else:
            return super(BaseCertificate, cls).__new__(cls)


class PfxCertificate(BaseCertificate):
    """Implementa a entidade do certificado eCNPJ A1, suportado pelo OpenSSL,
    e amplamente utilizado."""

    pfx = None

    def __init__(self, file_path: str, password: str):
        self.temp_files = []
        self._load_and_decripty_certificate(file_path, password)

    def _load_and_decripty_certificate(self, file_path: str, password: str):
        certificate_encrypted = PfxCertificate._load_certificate(file_path)
        self.pfx = PfxCertificate.decripty_certificate(certificate_encrypted, password)

    @staticmethod
    def _load_certificate(file_path):
        try:
            with open(file_path, "rb") as file_cert:
                return file_cert.read()
        except (PermissionError, FileNotFoundError) as exc:
            raise Exception(
                'Falha ao abrir arquivo do certificado digital A1. Verifique local e permissoes do arquivo.') from exc
        except Exception as exc:
            raise Exception('Falha ao abrir arquivo do certificado digital A1. Causa desconhecida.') from exc

    @staticmethod
    def decripty_certificate(cert_data, password):
        # Carrega o arquivo .pfx, pode gerar erro se a senha estive incorreta ou formato o arquivo for inválido.
        try:
            return crypto.load_pkcs12(cert_data, password)
        except crypto.Error as exc:
            raise Exception('Falha ao carregar certificado digital A1. Verifique a senha do certificado.') from exc
        except Exception as exc:
            raise Exception('Falha ao carregar certificado digital A1. Causa desconhecida.') from exc

    def generate_temp_files(self, certificate, certificate_key):
        with tempfile.NamedTemporaryFile(delete=False) as doc_certificate:
            doc_certificate.write(certificate)
        with tempfile.NamedTemporaryFile(delete=False) as doc_certificate_key:
            doc_certificate_key.write(certificate_key)
        self.temp_files.append(doc_certificate.name)
        self.temp_files.append(doc_certificate_key.name)
        return doc_certificate_key.name, doc_certificate.name

    def parse_to_pem(self):
        """Separa o arquivo de certificado em dois: chave e certificado no formato .pem,
        e retorna a string. Apos o uso devem ser excluidos com o metodo clear_temp_files."""

        certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, self.pfx.get_certificate())
        certificate_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, self.pfx.get_privatekey())

        return self.generate_temp_files(certificate, certificate_key)

    def is_valid(self):
        certificate = self.pfx.get_certificate()

        return certificate.has_expired() is False

    def clear_temp_files(self):
        try:
            for i in self.temp_files:
                os.remove(i)
            self.temp_files.clear()
        except:
            pass
