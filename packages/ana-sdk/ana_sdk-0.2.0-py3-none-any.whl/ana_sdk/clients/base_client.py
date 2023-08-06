from urllib.parse import urlencode

import requests


class BaseClient:

    @staticmethod
    def _dict_to_query_string(query_parameters: dict) -> str:
        """
        Recebe um dicionário de parâmetros e devolve uma string de consulta com seus parâmetros e valores.

        Args:
            query_parameters (dict): Dicionário de parâmetros.

        Returns:
            str: String de consulta gerada.
        """

        query_string = ""

        if query_parameters:
            query_string = "?" + urlencode(query_parameters)

        return query_string

    def _get_all_content(self, url: str) -> list[dict] | dict:
        """
        Faz uma requisição GET para uma URL e obtém todo o conteúdo paginado.

        Args:
            url (str): URL da requisição.

        Returns:
            list[dict] | dict: Conteúdo da resposta da requisição.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """
        
        headers = {"Authorization": f"Bearer {self._access_token}"}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()

        content = response.json()
        if "data" in content:
            next_page = content["next_page"]
            data = content["data"]

            while next_page:
                separator = "&" if "?" in url else "?"
                page = f"{url}{separator}page={next_page}"
                response = requests.get(url=page, headers=headers)
                content = response.json()
                data += content["data"]
                next_page = content["next_page"]

            return data
        else:
            return content
