class BaseRequester(object):

    _is_production = False  # True = Produção, False = Homologação
    _env = None
    uf = None
    certificate = None
    certificate_password = None
    url = None

    def __init__(self, uf: str, certificate: str, certificate_password: str, is_production=False):
        self.uf = uf.upper()
        self.certificate = certificate
        self.certificate_password = certificate_password
        self._is_production = is_production
        self._sefaz_env = 1 if is_production else 2
        self._env = 'PRD' if self._is_production else 'HML'

