from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.usuario_dto import UsuarioRequestDTO, UsuarioResponseDTO, UsuarioSenhaRequestDTO
from app.entities.enums import Perfil
from app.security.dependencias import UsuarioLogado, exigir_perfil, usuario_logado
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("", status_code=status.HTTP_201_CREATED)
def cadastrar(dto: UsuarioRequestDTO, db: Session = Depends(get_db)) -> UsuarioResponseDTO:
    return UsuarioService(db).cadastrar(dto)


@router.get("/existe")
def existe(login: str, db: Session = Depends(get_db)) -> bool:
    return UsuarioService(db).existe(login)


@router.get("/meus-dados")
def meus_dados(usuario: UsuarioLogado = Depends(usuario_logado), db: Session = Depends(get_db)) -> UsuarioResponseDTO:
    return UsuarioService(db).meus_dados(usuario.id)


@router.patch("/senha", status_code=status.HTTP_204_NO_CONTENT)
def alterar_senha(
    dto: UsuarioSenhaRequestDTO, usuario: UsuarioLogado = Depends(usuario_logado), db: Session = Depends(get_db)
) -> None:
    UsuarioService(db).alterar_senha(usuario.id, dto)


@router.get("/clientes", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def listar_clientes(db: Session = Depends(get_db)) -> list[UsuarioResponseDTO]:
    return UsuarioService(db).listar_clientes()
