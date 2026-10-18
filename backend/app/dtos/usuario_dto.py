from pydantic import BaseModel, ConfigDict, Field

from app.dtos.campos import TextoObrigatorio
from app.entities.enums import Perfil


class UsuarioRequestDTO(BaseModel):
    login: TextoObrigatorio = Field(max_length=100)
    senha: str = Field(min_length=1)
    perfil: Perfil


class UsuarioResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    perfil: Perfil


class UsuarioSenhaRequestDTO(BaseModel):
    senha: str = Field(min_length=1)
