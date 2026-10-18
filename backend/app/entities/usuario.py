from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.entities.enums import Perfil


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), unique=True)
    senha: Mapped[str] = mapped_column(String(255))
    # native_enum=False grava o nome do enum como texto (equivalente ao EnumType.STRING do JPA)
    perfil: Mapped[Perfil] = mapped_column(Enum(Perfil, native_enum=False, length=20))
