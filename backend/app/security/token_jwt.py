from datetime import datetime, timedelta, timezone

import jwt

from app.config import JWT_ALGORITHM, JWT_EXPIRACAO_HORAS, SECRET_KEY
from app.entities.usuario import Usuario


def gerar_token(usuario: Usuario) -> str:
    payload = {
        "sub": str(usuario.id),
        "login": usuario.login,
        "perfil": usuario.perfil.value,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRACAO_HORAS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Lança jwt.InvalidTokenError se o token for inválido ou estiver expirado."""
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
