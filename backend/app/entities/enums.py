from enum import StrEnum


class Perfil(StrEnum):
    CLIENTE = "CLIENTE"
    FUNCIONARIO = "FUNCIONARIO"


class Situacao(StrEnum):
    EM_ANDAMENTO = "EM_ANDAMENTO"
    FINALIZADA = "FINALIZADA"
