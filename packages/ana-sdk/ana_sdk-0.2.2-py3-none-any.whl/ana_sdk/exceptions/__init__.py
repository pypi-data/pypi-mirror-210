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
