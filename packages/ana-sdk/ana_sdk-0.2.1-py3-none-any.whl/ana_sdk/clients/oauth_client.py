import requests


class OAuthClient:
    """
    Classe para interagir com o cliente OAuth.

    Atributos:
        email (str): Email do usuário.
        _password (str): Senha do usuário.
        _token_url (str): URL completa do endpoint de obtenção do token.
    """

    def __init__(self, email: str, password: str, token_url: str):
        """
        Inicializa um objeto OAuthClient.

        Args:
            email (str): Email do usuário.
            password (str): Senha do usuário.
            token_url (str): URL completa do endpoint de obtenção do token.
        """

        self.email = email
        self._password = password
        self._token_url = token_url

    def get_token(self) -> dict[str, str]:
        """
        Obtém um token para o usuário associado a instância.

        Returns:
            str: Token de acesso.

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
        """

        data = {
            "client_id": "pontoweb",
            "username": self.email,
            "password": self._password,
            "grant_type": "password"
        }

        response = requests.post(
            self._token_url,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()

        return response.json()
