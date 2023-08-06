from ..clients.base_client import BaseClient


class DashboardAPIClient(BaseClient):
    """
    Classe para interagir com a API do Dashboard.

    Atributos:
        _access_token (str): Token de acesso para autenticação nas requisições.   
        _base_url (str): URL base da API do Dashboard.
    """

    def __init__(self, access_token: str, base_url: str):
        """
        Inicializa um objeto DashboardAPIClient.

        Args:
            access_token (str): Token de acesso para autenticação nas requisições.
            base_url (str): URL base da API do Dashboard.
        """

        self._access_token = access_token
        self._base_url = base_url

    def get_empresa(self, empresa_id: str | int) -> dict:
        """
        Obtém os detalhes de uma empresa pelo ID.

        Args:
            empresa_id (str | int): ID da empresa.

        Returns:
            dict: Detalhes da empresa.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        url = self._base_url + "/empresas/" + str(empresa_id)
        return self._get_all_content(url)

    def get_cliente(self, cliente_id: str | int) -> dict:
        """
        Obtém os detalhes de um cliente pelo ID.

        Args:
            cliente_id (str | int): ID do cliente.

        Returns:
            dict: Detalhes do cliente.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        url = self._base_url + "/clientes/" + str(cliente_id)
        return self._get_all_content(url)

    def get_tenant(self, tenant_id: str | int) -> dict:
        """
        Obtém os detalhes de um tenant pelo ID.

        Args:
            tenant_id (str | int): ID do tenant.

        Returns:
            dict: Detalhes do tenant.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        url = self._base_url + "/tenants/" + str(tenant_id)
        return self._get_all_content(url)

    def get_empresas(self, **query_string_parameters: dict) -> list[dict]:
        """
        Obtém uma lista de empresas com base nos parâmetros de consulta fornecidos.

        Args:
            query_string_parameters (dict): Parâmetros de consulta para filtrar empresas.

        Returns:
            list[dict]: Uma lista de empresas correspondentes aos parâmetros fornecidos.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        query_string = self._dict_to_query_string(query_string_parameters)
        url = self._base_url + "/empresas" + query_string
        return self._get_all_content(url)

    def get_clientes(self, **query_string_parameters: dict) -> list[dict]:
        """
        Obtém uma lista de clientes com base nos parâmetros de consulta fornecidos.

        Args:
            query_string_parameters (dict): Parâmetros de consulta para filtrar clientes.

        Returns:
            list[dict]: Uma lista de clientes correspondentes aos parâmetros fornecidos.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        query_string = self._dict_to_query_string(query_string_parameters)
        url = self._base_url + "/clientes" + query_string
        return self._get_all_content(url)

    def get_tenants(self, **query_string_parameters: dict) -> list[dict]:
        """
        Obtém uma lista de tenants com base nos parâmetros de consulta fornecidos.

        Args:
            query_string_parameters (dict): Parâmetros de consulta para filtrar tenants.

        Returns:
            list[dict]: Uma lista de tenants correspondentes aos parâmetros fornecidos.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        query_string = self._dict_to_query_string(query_string_parameters)
        url = self._base_url + "/tenants" + query_string
        return self._get_all_content(url)

    def get_tenant_by_empresa(self, empresa: dict) -> dict:
        """
        Obtém o tenant de uma empresa.

        Args:
            empresa (dict): Dados da empresa.

        Returns:
            dict: Dados do tenant da empresa.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        cliente = self.get_cliente(empresa["cliente_id"])
        return self.get_tenant(cliente["tenant_id"])
