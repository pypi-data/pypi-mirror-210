class ResultNotFoundError(Exception):
    """
    Exception destinada a informar que a task não possui resultado.
    """
    pass


class NoResultHandlerImplementedError(Exception):
    """
    Exception destinada a informar que o tipo de task executada não
    possui um ResultHandler implementado.
    """
    pass

class TaskError(Exception):
    """
    Exceptions destinada a lidar com erros obtidos durante a execução
    de uma task.

    Atributos:
        error_info (dict): Dicionário contendo chaves como `message` e
        `code`, entre outras específicas de cada task.
    """

    def __init__(self, error_info: dict, *args):
        self.error_info = error_info
        super().__init__(*args)
