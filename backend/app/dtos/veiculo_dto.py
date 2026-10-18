from pydantic import BaseModel, ConfigDict, Field

from app.dtos.campos import TextoObrigatorio


class VeiculoRequestDTO(BaseModel):
    placa: TextoObrigatorio = Field(max_length=20)
    descricao: TextoObrigatorio = Field(max_length=255)


class VeiculoDescricaoRequestDTO(BaseModel):
    """Usado no PATCH /veiculos/{id}: na alteração só a descrição pode mudar (R02)."""

    descricao: TextoObrigatorio = Field(max_length=255)


class VeiculoResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str
    descricao: str
    disponivel: bool
