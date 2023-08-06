import os
import time
from pprint import PrettyPrinter

from jsonschema import validate
from requests import HTTPError
from dotenv import load_dotenv

from .clients.oauth_client import OAuthClient
from .clients.dashboard_api_client import DashboardAPIClient
from .clients.rpa_api_client import RPAAPIClient
from .clients.ana_data_client import ANADataClient


class ANA:
    """
    A classe ANA fornece uma interface para interagir com os serviços
    relacionados ao ambiente de automação de negócios, dados e clientes.
    Permite realizar login, executar comandos, definir tenant, cliente
    e empresa atuais para ter acesso automático ao ANA Data.

    Atributos:
        current_empresa (dict): Dados da empresa atual.
        current_cliente (dict): Dados do cliente atual.
        current_tenant (dict): Dados do tenant atual.
        _auth (OAuthClient): Cliente de autenticação do OAuth.
        _access_token (str): Token de acesso gerado pelo OAuth.
        api (DashboardAPIClient): Cliente da Dashboard API que realiza
        consultas as dados dos clientes cadastrados na ANA.
        rpa (RPAAPIClient): Cliente da API de RPA da ANA, responsável
        por executar automações.
        data (ANADataClient): Cliente para interagir com os dados do ERP
        dos clientes ANA.
        ana_email (str): E-mail da ANA para requisições ao ANA-Data. É
        automaticamente carregada caso exista a variável de ambiente
        `ANA_EMAIL`.
        _ana_password (str): Senha da ANA para requisições ao ANA-Data.
        É automaticamente carregada caso exista a variável de ambiente
        `ANA_PASSWORD`.
        rpa_api_base_url (str): A URL base da RPA API.
        dashboard_api_base_url (str): A URL base da Dashboard API.
        oauth_token_full_url (str): A URL completa para obter o 
        token do usuário na API do OAuth.
    """

    current_empresa: dict = None
    current_cliente: dict = None
    current_tenant: dict = None

    api: DashboardAPIClient = None
    rpa: RPAAPIClient = None
    data: ANADataClient = None
    ana_email: str = None
    _ana_password: str = None

    rpa_api_base_url: str = None
    dashboard_api_base_url: str = None
    oauth_token_full_url: str = None

    _auth: OAuthClient = None
    _access_token: str = None

    def __init__(
        self,
        rpa_api_base_url: str = None,
        dashboard_api_base_url: str = None,
        oauth_token_full_url: str = None,
        ana_email: str = None,
        ana_password: str = None
    ):
        """
        Inicializa uma instância da classe ANA.

        Args:
            rpa_api_base_url (str): A URL base da RPA API. Tem precedência
            sobre a variável de ambiente `RPA_API_BASE_URL`
            dashboard_api_base_url (str): A URL base da Dashboard API. Tem
            precedência sobre a variável de ambiente `DASHBOARD_API_BASE_URL`
            oauth_token_full_url (str): A URL completa para obter o 
            token do usuário na API do OAuth. Tem precedência sobre a
            variável de ambiente `OAUTH_TOKEN_FULL_URL`
            ana_email (str): E-mail da ANA para requisições ao ANA-Data.
            Tem precedência sobre a variável de ambiente `ANA_EMAIL`.
            ana_password (str): Senha da ANA para requisições ao ANA-Data.
            Tem precedência sobre a variável de ambiente `ANA_PASSWORD`.

        Returns:
            None
        """

        load_dotenv()
        env_ana_email = os.getenv("ANA_EMAIL")
        env_ana_password = os.getenv("ANA_PASSWORD")

        if not ((ana_email or env_ana_email) and (ana_password or env_ana_password)):
            raise ValueError(
                "Defina as variáveis de ambiente [ANA_EMAIL] e [ANA_PASSWORD] "
                "ou instancie a classe passando [ana_email] e [ana_password] "
                "como parâmetros para o construtor."
            )
        
        env_rpa_api_base_url = os.getenv("RPA_API_BASE_URL")
        env_dashboard_api_base_url = os.getenv("DASHBOARD_API_BASE_URL")
        env_oauth_token_full_url = os.getenv("OAUTH_TOKEN_FULL_URL")

        if not (
            (rpa_api_base_url or env_rpa_api_base_url)
            and (dashboard_api_base_url or env_dashboard_api_base_url)
            and (oauth_token_full_url or env_oauth_token_full_url)
        ):
            raise ValueError(
                "Defina as variáveis de ambiente [RPA_API_BASE_URL], "
                "[DASHBOARD_API_BASE_URL] e [OAUTH_TOKEN_FULL_URL] "
                "ou instancie a classe passando [rpa_api_base_url], "
                "[dashboard_api_base_url] e [oauth_token_full_url] "
                "como parâmetros para o construtor."
            )

        self.ana_email = ana_email or env_ana_email
        self._ana_password = ana_password or env_ana_password
        
        self.rpa_api_base_url = rpa_api_base_url or env_rpa_api_base_url
        self.dashboard_api_base_url = dashboard_api_base_url or env_dashboard_api_base_url
        self.oauth_token_full_url = oauth_token_full_url or env_oauth_token_full_url

    def login(self, email: str, password: str):
        """
        Realiza o login do usuário com as credenciais fornecidas,
        obtendo o token de acesso e configurando os clientes para
        interagir com os serviços fornecidos.

        Args:
            email (str): O email do usuário.
            password (str): A senha do usuário.

        Returns:
            None

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisição.
            ValueError: Caso email e senha não tenham sido passados nem
            encontrados nas variáveis de ambiente.
        """

        load_dotenv()
        env_user_email = os.getenv("USER_EMAIL")
        env_user_password = os.getenv("USER_PASSWORD")

        if not ((email or env_user_email) and (password or env_user_password)):
            raise ValueError(
                "Defina as variáveis de ambiente [USER_EMAIL] e [USER_PASSWORD] "
                "ou chame o método passando [email] e [password] "
                "como parâmetros."
            )

        self._auth = OAuthClient(
            email or env_user_email,
            password or env_user_password,
            self.oauth_token_full_url
        )
        self._access_token = self._auth.get_token()["access_token"] 

        self.api = DashboardAPIClient(self._access_token, self.dashboard_api_base_url)
        self.rpa = RPAAPIClient(self._access_token, self.rpa_api_base_url)

    def logout(self):
        """
        Faz o logout do usuário, limpando todas as informações.

        Returns:
            None
        """

        self._auth = None
        self._access_token = None
        
        self.api = None
        self.rpa = None
        self.data = None

        self.current_empresa = None
        self.current_cliente = None
        self.current_tenant = None

    def help(self, mope: str = None) -> dict[str, str]:
        """
        Exibe informações sobre os comandos disponíveis para automação.
        Se um MOPE for fornecido, exibe o JSON Schema do comando
        relacionado.

        Args:
            mope (str, optional): O MOPE do comando. Se não fornecido,
            exibe informações sobre todos os comandos disponíveis.

        Returns:
            dict: JSON Schema do MOPE informado, ou lista com todos
            os comandos disponíveis na RPA API, caso não seja informado
            nenhum MOPE.
        """

        self._ana_cli_logo()

        if not mope:
            response = self.rpa.get_comandos()

            if response:
                print('Comandos disponíveis:')
                for comando in response:
                    print('MOPE: {} - Comando: {}'.format(comando['codigo_mope'], comando['nome_automacao']))

        else:
            printer = PrettyPrinter()
            response = self.rpa.get_json_schema(mope)
            printer.pprint(response)

        return response

    def _ana_cli_logo(self):
        print("""
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            %%%%%%%%%%%%%         %%%%%%%%%        %%%%%%%     %%%%%%%%         %%%%%%%%%%%%
            %%%%%%%%%%%%           %%%%%%%%          %%%%%     %%%%%%%           %%%%%%%%%%%
            %%%%%%%%%%%      %%      %%%%%%     %      %%%     %%%%%%     %%      %%%%%%%%%%
            %%%%%%%%%%      %%%%      %%%%%     %%%      %     %%%%%     %%%%      %%%%%%%%%
            %%%%%%%%%      %%%%%%%      %%%     %%%%%%         %%%      %%%%%%      %%%%%%%%
            %%%%%%%%      %%%%%%%%%      %%     %%%%%%%%       %%      %%%%%%%%%     %%%%%%%
            %%%%%%%      %%%%%%%%%%%            %%%%%%%%%%            %%%%%%%%%%%     %%%%%%
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        """)

    def set_tenant(self, id: int) -> None:
        """
        Define o tenant atual com base no ID fornecido. Configura o
        cliente do ANA Data.
        
        Args:
            id (int): O ID do tenant.

        Returns:
            None

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer as requisições.
        """

        self.current_tenant = self.api.get_tenant(id)
        self.data = ANADataClient(
            self.ana_email,
            self._ana_password,
            self.current_tenant["configuracoes"]["ana_data_base_url"],
            self.oauth_token_full_url
        )

    def set_cliente(self, id: int) -> None:
        """
        Define o cliente atual com base no ID fornecido. Obtém o
        tenant associado ao cliente e chama o método set_tenant()
        para configurar o ANA Data.
        
        Args:
            id (int): O ID do cliente.

        Returns:
            None

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer as requisições.
        """

        self.current_cliente = self.api.get_cliente(id)
        self.set_tenant(self.api.get_tenant(self.current_cliente["tenant_id"])["id"])

    def set_empresa(self, id: int) -> None:
        """
        Define a empresa atual com base no ID fornecido. Obtém o
        cliente associado à empresa e chama o método set_cliente()
        para configurar o ANA Data.
        
        Args:
            id (int): O ID da empresa.

        Returns:
            None

        Raises:
            requests.HTTPError: Se ocorrer um erro ao fazer a requisições.
        """
        
        self.current_empresa = self.api.get_empresa(id)
        self.set_cliente(self.api.get_cliente(self.current_empresa["cliente_id"])["id"])
        self.set_tenant(self.api.get_tenant(self.current_cliente["tenant_id"])["id"])

    def _wait_for_task(self, task_id: str) -> dict | None:
        """
        Aguarda a conclusão de uma task.

        Args:
            task_id (str): O ID da task a ser aguardada.

        Returns:
            dict | None: Um dicionário contendo informações sobre a
            tarefa concluída, se a tarefa for encontrada e estiver
            concluída com sucesso ou falha. Retorna None se a tarefa
            não for encontrada.

        Raises:
            requests.HTTPError: Se ocorrer um erro durante a consulta
            à API de status de tasks ou o limite de tentativas for
            excedido.
        """

        max_attempts = 5
        not_found_count = 0
        finished = False
        task = None

        while not finished:
            try:
                task = self.rpa.get_task(task_id)
                if task.get("status") in ("SUCCESS", "FAILURE"):
                    finished = True
            
            except HTTPError as e:
                if e.response.status_code == 404:
                    if not_found_count < max_attempts:
                        not_found_count += 1
                        time.sleep(5)
                    else:
                        raise e
                else:
                    raise e

        return task

    def execute(
        self,
        mope: str,
        data: dict,
        wait_for_task: bool = True
    ) -> tuple[dict, dict] | dict:
        """
        Executa o comando identificado pelo MOPE passado utilizando os
        dados passados.

        Envia uma requisição para que a RPA API execute um comando
        com base no MOPE e nos dados fornecidos. Valida os dados em
        relação ao JSON Schema antes de fazer a requisição.
        Espera a conclusão da tarefa de automação por padrão e retorna
        o resultado obtido. Pode não esperar pela conclusão, caso a
        flag `wait_for_task` seja passada como `False`. Nesse caso,
        retorna um dicionário com a resposta da API e o ID da task.
        

        Args:
            mope (str): O MOPE do comando.
            data (dict): Os dados necessários para o comando de automação.
            wait_for_task (bool): Se deve ou não esperar pela conclusão
            de forma síncrona.

        Returns:
            tuple[dict, dict]: O resultado da automação e a resposta da
            RPA API no ato do enfileiramento do comando, para propósitos
            de debug.

        Raises:
            Exception: Se a tarefa de automação falhar, uma exceção
            será levantada com a mensagem de erro gerada pela automação.
            jsonschema.ValidationError: Se a pré-validação dos dados
            falhar.
        """

        schema = self.rpa.get_json_schema(mope)
        validate(instance=data, schema=schema)
        
        response = self.rpa.execute_command(mope, data)
        task_id = response.get("job_id")

        if wait_for_task:
            task = self._wait_for_task(task_id)

            if task['status'] == "FAILURE":
                raise Exception(task['erro'])
            else:
                return (task['result'], response)
        
        else:
            return response
