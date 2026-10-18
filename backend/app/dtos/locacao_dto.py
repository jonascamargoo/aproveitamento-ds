from pydantic import BaseModel

from app.entities.enums import Situacao


class LocacaoRequestDTO(BaseModel):
    # funcionarioId não é informado: vem do token JWT
    veiculoId: int
    clienteId: int


class LocacaoResponseDTO(BaseModel):
    id: int
    veiculoId: int
    situacao: Situacao
    clienteId: int
    funcionarioId: int
