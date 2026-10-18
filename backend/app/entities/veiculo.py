from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Veiculo(Base):
    __tablename__ = "veiculo"

    id: Mapped[int] = mapped_column(primary_key=True)
    placa: Mapped[str] = mapped_column(String(20), unique=True)
    descricao: Mapped[str] = mapped_column(String(255))
    disponivel: Mapped[bool] = mapped_column(default=True)
