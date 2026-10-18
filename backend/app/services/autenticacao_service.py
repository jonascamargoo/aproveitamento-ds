from sqlalchemy.orm import Session

from app.dtos.autenticacao_dto import AutenticacaoRequestDTO, AutenticacaoResponseDTO
from app.exceptions import CredenciaisInvalidasException
from app.repositories.usuario_repository import UsuarioRepository
from app.security.senha import verificar_senha
from app.security.token_jwt import gerar_token


class AutenticacaoService:
    def __init__(self, db: Session):
        self.usuario_repository = UsuarioRepository(db)

    def autenticar(self, dto: AutenticacaoRequestDTO) -> AutenticacaoResponseDTO:
        usuario = self.usuario_repository.buscar_por_login(dto.login)
        if usuario is None or not verificar_senha(dto.senha, usuario.senha):
            raise CredenciaisInvalidasException("Login ou senha inválidos")
        return AutenticacaoResponseDTO(token=gerar_token(usuario))
