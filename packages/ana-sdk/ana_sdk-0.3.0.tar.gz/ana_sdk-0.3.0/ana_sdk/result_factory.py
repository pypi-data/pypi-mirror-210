from __future__ import annotations

from abc import ABC
from pathlib import Path

import requests

from .exceptions import (
    ResultNotFoundError,
    NoResultHandlerImplementedError,
    TaskError,
)


class AbstractResultHandler(ABC):
    """
    Classe abstrata utilizada como interface para todos os manipuladores
    de resultado.
    """

    _result: dict = None
    status: str = None
    error: dict = None
    meta: dict = None

    def __init__(self, result: dict) -> None:
        """
        Construtor da classe.

        Args:
            result (dict): O resultado a ser processado.
        """

        self._result = result

    def get_result(self) -> AbstractResultHandler:
        """
        Método abstrato para obter o resultado.
        """
        pass


class Report(AbstractResultHandler):
    """
    Classe que lida com resultados de execuções de relatórios.

    Atributos (disponíveis após o uso do método `get_result()`):
        status (str): Status de conclusão do relatório, sendo "SUCCESS",
        "FAILURE" ou "ERROR".
        error (dict): Detalhamento de erro, caso status seja diferente
        de "SUCCESS".
        meta (dict): Metadados da execução.
        file (dict): Informações sobre o arquivo gerado.
    """

    file: dict = None
    
    def get_result(self) -> Report:
        """
        Obtém o resultado da execução de um relatório.

        Returns:
            Report: A instância atual da classe Report, possibilitando
            method chaining.
        """
        
        self.file = self._result["data"]["file"]
        self.error = self._result["error"]
        self.meta = self._result["meta"]
        self.status = self._result["status"]

        return self
    
    def save_to_path(self, path: str, new_filename: str = None) -> Report:
        """
        Salva o relatório em um determinado caminho.

        É possível também nomear o arquivo como desejado.

        Args:
            path (str): O caminho onde o relatório será salvo.
            new_filename (str, optional): O novo nome do arquivo. Se
            não for fornecido, o nome original será usado.

        Returns:
            Report: A instância atual da classe Report, possibilitando
            method chaining.
        """
        if self.file:
            if self.file["type"] == "url":
                url = self.file["link"]
                filename = new_filename or self.file["name"]
                filename_with_extension = filename + "." + self.file["extension"]

                Path(path).mkdir(parents=True, exist_ok=True)
                full_filename = path if path.endswith("/") else (path + "/") + filename_with_extension

                response = requests.get(url)
                response.raise_for_status()

                with open(full_filename, "w") as file:
                    file.write(response.text)

        return self
    
    def get_link(self) -> str | None:
        """
        Recupera o link do relatório, caso exista um.

        Returns:
            str: Link do relatório, caso exista. Ou `None`.
        """
        return self.file.get("link") 


class Task(AbstractResultHandler):
    """
    Classe que lida com resultados de execuções de tasks que não geram
    relatórios.
    """

    response: dict = None
    
    def get_result(self) -> Task:
        pass


class ResultFactory:
    """
    Factory para criar os manipuladores de resultado.
    """

    @staticmethod
    def create_result_handler(task_info: dict) -> Report | Task:
        """
        Cria um manipulador de resultado com base nas informações da tarefa.

        Args:
            task_info (dict): As informações da tarefa.

        Returns:
            AbstractResultHandler: O manipulador de resultado correspondente.
        
        Raises:
            ResultNotFoundError: Se o resultado não estiver presente nas
            informações da tarefa.
            NoResultHandlerImplementedError: Se não houver um manipulador
            de resultado implementado para o tipo de resultado em questão.
            TaskError: Se a task apresentar algum erro. Contém o dicionário
            de erro enviado pela RPA API.
        """

        result: dict = task_info.get("result")
        if not result:
            raise ResultNotFoundError()
        
        data: dict = result.get("data")
        status: str = result.get("status")
        if status in ("ERROR", "FAILURE"):
            raise TaskError(result.get("error"))
        
        if data and "file" in data.keys():
            return Report(result)
        elif data and data.get("response"):
            return Task(result)
        else:
            raise NoResultHandlerImplementedError()
