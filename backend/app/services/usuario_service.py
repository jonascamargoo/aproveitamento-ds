from sqlalchemy.orm import Session

from app.dtos.usuario_dto import UsuarioRequestDTO, UsuarioResponseDTO, UsuarioSenhaRequestDTO
from app.entities.enums import Perfil
from app.entities.usuario import Usuario
from app.exceptions import ConflitoException, NaoEncontradoException
from app.repositories.usuario_repository import UsuarioRepository
from app.security.senha import gerar_hash


class UsuarioService:
    def __init__(self, db: Session):
        self.repository = UsuarioRepository(db)

    def cadastrar(self, dto: UsuarioRequestDTO) -> UsuarioResponseDTO:
        # R01 - login único
        if self.repository.existe_por_login(dto.login):
            raise ConflitoException("Já existe um usuário com este login")
        usuario = Usuario(login=dto.login, senha=gerar_hash(dto.senha), perfil=dto.perfil)
        return UsuarioResponseDTO.model_validate(self.repository.salvar(usuario))

    def existe(self, login: str) -> bool:
        return self.repository.existe_por_login(login)

    def meus_dados(self, usuario_id: int) -> UsuarioResponseDTO:
        return UsuarioResponseDTO.model_validate(self._buscar_entidade(usuario_id))

    def alterar_senha(self, usuario_id: int, dto: UsuarioSenhaRequestDTO) -> None:
        usuario = self._buscar_entidade(usuario_id)
        usuario.senha = gerar_hash(dto.senha)
        self.repository.salvar(usuario)

    def listar_clientes(self) -> list[UsuarioResponseDTO]:
        return [UsuarioResponseDTO.model_validate(u) for u in self.repository.listar_por_perfil(Perfil.CLIENTE)]

    def _buscar_entidade(self, id: int) -> Usuario:
        usuario = self.repository.buscar_por_id(id)
        if usuario is None:
            raise NaoEncontradoException("Usuário não encontrado")
        return usuario
