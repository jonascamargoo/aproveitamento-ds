class NegocioException(Exception):
    """Regra de negócio violada (HTTP 400). As subclasses só mudam o status HTTP.

    O handler em main.py converte qualquer uma delas em {"detail": mensagem}.
    """

    status_code = 400

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class CredenciaisInvalidasException(NegocioException):
    status_code = 401


class AcessoNegadoException(NegocioException):
    status_code = 403


class NaoEncontradoException(NegocioException):
    status_code = 404


class ConflitoException(NegocioException):
    status_code = 409
