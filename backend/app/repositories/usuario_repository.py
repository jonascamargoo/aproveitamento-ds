from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.enums import Perfil
from app.entities.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def buscar_por_id(self, id: int) -> Usuario | None:
        return self.db.get(Usuario, id)

    def buscar_por_login(self, login: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.login == login))

    def existe_por_login(self, login: str) -> bool:
        return self.buscar_por_login(login) is not None

    def listar_por_perfil(self, perfil: Perfil) -> list[Usuario]:
        return list(self.db.scalars(select(Usuario).where(Usuario.perfil == perfil).order_by(Usuario.id)))
