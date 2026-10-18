from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.locacao import Locacao


class LocacaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, locacao: Locacao) -> Locacao:
        self.db.add(locacao)
        self.db.commit()
        self.db.refresh(locacao)
        return locacao

    def buscar_por_id(self, id: int) -> Locacao | None:
        return self.db.get(Locacao, id)

    def listar_por_cliente(self, cliente_id: int) -> list[Locacao]:
        return list(self.db.scalars(select(Locacao).where(Locacao.cliente_id == cliente_id).order_by(Locacao.id)))

    def listar_por_funcionario(self, funcionario_id: int) -> list[Locacao]:
        return list(
            self.db.scalars(select(Locacao).where(Locacao.funcionario_id == funcionario_id).order_by(Locacao.id))
        )

    def existe_por_veiculo(self, veiculo_id: int) -> bool:
        return self.db.scalar(select(Locacao.id).where(Locacao.veiculo_id == veiculo_id).limit(1)) is not None
