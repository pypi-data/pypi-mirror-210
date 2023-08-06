from .nfe_xml_builder_factory import NfeXmlBuilderFactory

#Classe builder principal que ira encapsular o método de instanciamento da classe builder e chamada do método


class NfeXmlBuilder:

    @staticmethod
    def build(class_type, **kwargs):
        class_builder = NfeXmlBuilderFactory.get_builder(class_type, **kwargs)
        return class_builder.build()
