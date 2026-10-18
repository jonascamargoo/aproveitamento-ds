from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.veiculo_dto import VeiculoDescricaoRequestDTO, VeiculoRequestDTO, VeiculoResponseDTO
from app.entities.enums import Perfil
from app.security.dependencias import exigir_perfil, usuario_logado
from app.services.veiculo_service import VeiculoService

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


@router.get("", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def listar(db: Session = Depends(get_db)) -> list[VeiculoResponseDTO]:
    return VeiculoService(db).listar()


# Precisa vir antes de /{id}, senão "existe" seria tratado como id
@router.get("/existe", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def existe(placa: str, db: Session = Depends(get_db)) -> bool:
    return VeiculoService(db).existe(placa)


@router.get("/{id}", dependencies=[Depends(usuario_logado)])
def buscar(id: int, db: Session = Depends(get_db)) -> VeiculoResponseDTO:
    return VeiculoService(db).buscar(id)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def cadastrar(dto: VeiculoRequestDTO, db: Session = Depends(get_db)) -> VeiculoResponseDTO:
    return VeiculoService(db).cadastrar(dto)


@router.patch("/{id}", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def alterar_descricao(id: int, dto: VeiculoDescricaoRequestDTO, db: Session = Depends(get_db)) -> VeiculoResponseDTO:
    return VeiculoService(db).alterar_descricao(id, dto)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def excluir(id: int, db: Session = Depends(get_db)) -> None:
    VeiculoService(db).excluir(id)
