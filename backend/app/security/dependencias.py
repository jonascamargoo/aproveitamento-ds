from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.entities.enums import Perfil
from app.repositories.usuario_repository import UsuarioRepository
from app.security.token_jwt import decodificar_token

bearer = HTTPBearer(auto_error=False)


@dataclass
class UsuarioLogado:
    """Usuário autenticado, identificado pelo JWT. É o que os controllers recebem (nunca a entidade)."""

    id: int
    login: str
    perfil: Perfil


def usuario_logado(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> UsuarioLogado:
    """Exige um token válido (401 caso contrário) e devolve o usuário dono do token."""
    if credenciais is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token não informado")
    try:
        payload = decodificar_token(credenciais.credentials)
        # Confere no banco se o usuário ainda existe (ex.: token antigo depois de apagar o ocar.db)
        usuario = UsuarioRepository(db).buscar_por_id(int(payload["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        usuario = None
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado")
    return UsuarioLogado(id=usuario.id, login=usuario.login, perfil=usuario.perfil)


def exigir_perfil(*perfis: Perfil):
    """Uso: Depends(exigir_perfil(Perfil.FUNCIONARIO)). Devolve o usuário logado ou 403."""

    def verificar(usuario: UsuarioLogado = Depends(usuario_logado)) -> UsuarioLogado:
        if usuario.perfil not in perfis:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado para o seu perfil")
        return usuario

    return verificar
