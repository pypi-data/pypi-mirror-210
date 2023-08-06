from .nfe_xml_builder_base import NfeXmlBuilderBase
from .nfe_xml_builder_status import NfeXmlBuilderStatus
from .nfe_xml_builder_distribution import NfeXmlBuilderDistribution

# Classe factory que define e instancia a classe de builder que ira gerar o xml


BUILDERS_LIST = {
    'STATUS': NfeXmlBuilderStatus,
    'DISTRIBUICAO': NfeXmlBuilderDistribution
}


class NfeXmlBuilderFactory:
    @staticmethod
    def get_builder(class_type: str, **kwargs) -> NfeXmlBuilderBase:
        class_type = BUILDERS_LIST[class_type] if BUILDERS_LIST[class_type] else NfeXmlBuilderStatus
        return class_type(**kwargs)
