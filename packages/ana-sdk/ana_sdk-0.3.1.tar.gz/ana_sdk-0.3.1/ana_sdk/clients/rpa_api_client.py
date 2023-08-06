import requests

from ..clients.base_client import BaseClient


class RPAAPIClient(BaseClient):
    """
    Classe para interagir com o cliente RPA API.

    Atributos:
        _access_token (str): Token de acesso para autenticação nas requisições.
        _base_url (str): URL base da API do RPA.
    """

    def __init__(self, access_token: str, base_url: str):
        """
        Inicializa um objeto RPAAPIClient.

        Args:
            access_token (str): Token de acesso para autenticação nas requisições.
            base_url (str): URL base da API do Dashboard.
        """

        self._access_token = access_token
        self._base_url = base_url

    def get_comandos(self) -> list[dict]:
        """
        Obtém os comandos disponíveis.

        Returns:
            list[dict]: Lista de comandos disponíveis.
        """

        url = self._base_url + "/jobs"
        return self._get_all_content(url)

    def get_json_schema(self, mope: str) -> dict:
        """
        Obtém o esquema JSON para um determinado comando.

        Args:
            mope (str): Identificador do comando.

        Returns:
            dict: Esquema JSON do comando.
        """

        url = self._base_url + f"/jobs/{mope}/schema"
        return self._get_all_content(url)

    def get_task(self, task_id: str) -> dict:
        """
        Obtém informações sobre uma tarefa específica.

        Args:
            task_id (str): ID da tarefa.

        Returns:
            dict: Informações da tarefa.
        """

        url = self._base_url + f"/tasks/{task_id}"
        return self._get_all_content(url)

    def get_tasks(self, **query_string_parameters) -> dict:
        """
        Obtém as tarefas com base nos parâmetros de string de consulta fornecidos.

        Args:
            **query_string_parameters: Parâmetros de string de consulta para filtrar as tarefas.

        Returns:
            dict: Tarefas correspondentes aos parâmetros de string de consulta.
        """

        query_string = self._dict_to_query_string(query_string_parameters)
        url = self._base_url + f"/tasks" + query_string
        return self._get_all_content(url)

    def get_task_status(self, task_id: str) -> dict:
        """
        Obtém o status de uma tarefa específica.

        Args:
            task_id (str): ID da tarefa.

        Returns:
            dict: Status da tarefa.
        """

        url = self._base_url + f"/jobs/{task_id}/status"
        return self._get_all_content(url)

    def execute_command(self, mope: str, data: dict) -> dict:
        """
        Executa um comando.

        Args:
            mope (str): Identificador do comando.
            data (dict): Dados para o comando.

        Returns:
            dict: Resultado da execução do comando.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        headers = {"Authorization": f"Bearer {self._access_token}"}
        url = self._base_url + f"/jobs/{mope}"
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()

        content = response.json()

        return content
