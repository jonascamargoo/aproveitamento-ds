from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.entities.enums import Situacao
from app.entities.usuario import Usuario
from app.entities.veiculo import Veiculo


class Locacao(Base):
    __tablename__ = "locacao"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relacionamentos muitos-para-um: a coluna *_id + relationship() equivalem ao @ManyToOne/@JoinColumn do JPA
    veiculo_id: Mapped[int] = mapped_column(ForeignKey("veiculo.id"))
    veiculo: Mapped[Veiculo] = relationship()

    situacao: Mapped[Situacao] = mapped_column(
        Enum(Situacao, native_enum=False, length=20), default=Situacao.EM_ANDAMENTO
    )

    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    cliente: Mapped[Usuario] = relationship(foreign_keys=[cliente_id])

    funcionario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    funcionario: Mapped[Usuario] = relationship(foreign_keys=[funcionario_id])
