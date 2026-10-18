from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.veiculo import Veiculo


class VeiculoRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, veiculo: Veiculo) -> Veiculo:
        self.db.add(veiculo)
        self.db.commit()
        self.db.refresh(veiculo)
        return veiculo

    def excluir(self, veiculo: Veiculo) -> None:
        self.db.delete(veiculo)
        self.db.commit()

    def buscar_por_id(self, id: int) -> Veiculo | None:
        return self.db.get(Veiculo, id)

    def listar(self) -> list[Veiculo]:
        return list(self.db.scalars(select(Veiculo).order_by(Veiculo.id)))

    def existe_por_placa(self, placa: str) -> bool:
        return self.db.scalar(select(Veiculo.id).where(Veiculo.placa == placa)) is not None
