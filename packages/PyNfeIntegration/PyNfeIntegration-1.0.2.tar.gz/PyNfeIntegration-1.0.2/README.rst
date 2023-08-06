PyNfeIntegration
======

PyNfeIntegration is a library to implement functionalities to consult and download invoices generate against some CNPJ

- NfeRequester: Class to consult status of services and invoices generated against some CNPJ

Example of use:
______
    def test_consult():
        certificate = "/certificate_path.pfx"
        password = 'certificate_password'
        uf = 'sp'
        production = True

        con = NFeRequester(uf, certificate, password, production)
        soap_xml = con.consult_invoices(cnpj='cnpj_number')
        print(soap_xml.text)

    test_consult()


Install
-------

pip install PyNfeIntegration