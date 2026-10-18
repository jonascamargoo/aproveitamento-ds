from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.locacao_dto import LocacaoRequestDTO, LocacaoResponseDTO
from app.entities.enums import Perfil
from app.security.dependencias import UsuarioLogado, exigir_perfil, usuario_logado
from app.services.locacao_service import LocacaoService

router = APIRouter(prefix="/locacoes", tags=["Locações"])


@router.post("", status_code=status.HTTP_201_CREATED)
def criar(
    dto: LocacaoRequestDTO,
    funcionario: UsuarioLogado = Depends(exigir_perfil(Perfil.FUNCIONARIO)),
    db: Session = Depends(get_db),
) -> LocacaoResponseDTO:
    return LocacaoService(db).criar(dto, funcionario.id)


# Precisa vir antes de /{id}, senão "minhas" seria tratado como id
@router.get("/minhas")
def listar_minhas(
    usuario: UsuarioLogado = Depends(usuario_logado), db: Session = Depends(get_db)
) -> list[LocacaoResponseDTO]:
    return LocacaoService(db).listar_minhas(usuario.id, usuario.perfil)


@router.get("/{id}")
def buscar(id: int, usuario: UsuarioLogado = Depends(usuario_logado), db: Session = Depends(get_db)) -> LocacaoResponseDTO:
    return LocacaoService(db).buscar(id, usuario.id, usuario.perfil)


@router.patch("/{id}/finalizar")
def finalizar(
    id: int,
    funcionario: UsuarioLogado = Depends(exigir_perfil(Perfil.FUNCIONARIO)),
    db: Session = Depends(get_db),
) -> LocacaoResponseDTO:
    return LocacaoService(db).finalizar(id, funcionario.id)
