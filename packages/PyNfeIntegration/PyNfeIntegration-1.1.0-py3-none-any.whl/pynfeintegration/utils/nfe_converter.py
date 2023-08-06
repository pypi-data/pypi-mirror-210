import gzip
import base64
import xml.etree.ElementTree as et


class NfeConverter:

    @staticmethod
    def _remove_namespace(tag):
        return tag.split('}', 1)[1] if '}' in tag else tag

    @staticmethod
    def extract_to_xml(base64_content):
        # Decodificar o conteúdo base64
        decoded_content = base64.b64decode(base64_content)
        # Descompactar o conteúdo GZIP
        uncompressed_data = gzip.decompress(decoded_content)

        return et.fromstring(uncompressed_data)

    @staticmethod
    def xml_to_json(xml: et):
        # Converter o XML em um objeto JSON
        json_data = {
            NfeConverter._remove_namespace(xml.tag): xml.attrib,
            'content': {}
        }

        for child in xml:
            json_data['content'][NfeConverter._remove_namespace(child.tag)] = child.text

        # Converter o objeto JSON em uma string

        return json_data
