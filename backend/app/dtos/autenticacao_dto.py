from pydantic import BaseModel, Field

from app.dtos.campos import TextoObrigatorio


class AutenticacaoRequestDTO(BaseModel):
    login: TextoObrigatorio
    senha: str = Field(min_length=1)


class AutenticacaoResponseDTO(BaseModel):
    token: str
