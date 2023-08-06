import requests

from ..clients.oauth_client import OAuthClient
from ..clients.base_client import BaseClient


class ANADataClient(BaseClient):
    """
    Classe para interagir com a API do ANA Data.

    Attributes:
        ana_data_base_url (str): A URL base da API do ANA Data.
        _auth (OAuthClient): Objeto cliente OAuth para autenticação.
        _access_token (str): Token de acesso para autorização na API.

    """

    def __init__(
        self,
        email_ana: str,
        password_ana: str,
        ana_data_base_url: str,
        oauth_token_full_url: str
    ):
        """
        Inicializa uma nova instância do ANADataClient.

        Args:
            ana_data_base_url (str): A URL base da API do ANA Data.
            email_ana (str): Email para autenticação na API do ANA Data.
            password_ana (str): Senha para autenticação na API do ANA Data.
            oauth_token_full_url (str): URL completa do endpoint de obtenção do token.
        """

        self.ana_data_base_url = ana_data_base_url
        self._auth = OAuthClient(email_ana, password_ana, oauth_token_full_url)
        self._access_token = self._auth.get_token()["access_token"]
    
    def _get_all_content(self, url: str) -> list[dict] | dict:
        """
        Obtém todo o conteúdo paginado de uma URL.

        Args:
            url (str): A URL para obter o conteúdo.

        Returns:
            list[dict] | dict: O conteúdo obtido da URL.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        headers = {"Authorization": f"Bearer {self._access_token}"}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()

        content = response.json()
        if "results" in content:
            next_page = content["next"]
            results = content["results"]

            while next_page:
                separator = "&" if "?" in url else "?"
                page = f"{url}{separator}page={next_page}"
                response = requests.get(url=page, headers=headers)
                content = response.json()
                results += content["results"]
                next_page = content["next"]

            return results
        else:
            return content

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
        url = self.ana_data_base_url + "/persona/empresas" + query_string
        return self._get_all_content(url)
    
    def get_lotacoes(self, **query_string_parameters: dict) -> list[dict]:
        """
        Obtém uma lista de lotações com base nos parâmetros de consulta fornecidos.

        Args:
            query_string_parameters (dict): Parâmetros de consulta para filtrar lotações.

        Returns:
            list[dict]: Uma lista de lotações correspondentes aos parâmetros fornecidos.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        query_string = self._dict_to_query_string(query_string_parameters)
        url = self.ana_data_base_url + "/persona/lotacoes" + query_string
        return self._get_all_content(url)
    
    def get_trabalhadores(self, **query_string_parameters: dict) -> list[dict]:
        """
        Obtém uma lista de trabalhadores com base nos parâmetros de consulta fornecidos.

        Args:
            query_string_parameters (dict): Parâmetros de consulta para filtrar trabalhadores.

        Returns:
            list[dict]: Uma lista de trabalhadores correspondentes aos parâmetros fornecidos.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        query_string = self._dict_to_query_string(query_string_parameters)
        url = self.ana_data_base_url + "/persona/trabalhadores" + query_string
        return self._get_all_content(url)
